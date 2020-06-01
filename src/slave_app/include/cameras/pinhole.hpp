#pragma once

#include "camera.hpp"

namespace poly::camera {

    class PinholeCamera : public Camera {
    public:
        float m_d;

        PinholeCamera(float d)
        {
          m_d = d;
        }

        Colour colour_validate(Colour const& colour) const
        {
          if (colour.x > 1.0f
              || colour.y > 1.0f
              || colour.z > 1.0f
              || colour.x < 0.0f
              || colour.y < 0.0f
              || colour.z < 0.0f)
          {
            // Out of gamut turns RED
            return Colour(1.0f, 0.0f, 0.0f);
          }
          else {
            return colour;
          }
        }

        void multithread_render_scene(poly::structures::World& world, unsigned int num_threads)
        {
          int wheight = (int)world.m_vp->vres;
          int wwidth = (int)world.m_vp->hres;

          // vector for which we will allow threads to read from an retrieve slabs to render
          std::shared_ptr<std::mutex> slablist_mutex = std::make_shared<std::mutex>();
          std::vector<std::shared_ptr<poly::structures::scene_slab>> slabs;

          std::shared_ptr<std::vector<std::vector<Colour>>> storage = std::make_shared<std::vector<std::vector<Colour>>>(world.m_vp->vres, std::vector<Colour>(world.m_vp->hres));
          std::shared_ptr<std::mutex> storage_mutex = std::make_shared<std::mutex>();
          std::vector<std::thread> thread_list;

          std::shared_ptr<poly::structures::World> world_ptr = std::make_shared<poly::structures::World>(world);

          int slab_width = world.m_slab_size;
          int slab_height = world.m_slab_size;

          for (int i = world.m_start_height; i < world.m_end_height; i += world.m_slab_size)
          {
            // Reset slab width on each height loop
            slab_width = world.m_slab_size;

            // Check that we aren't flying off the bottom of our image
            if (i + slab_height > wheight) {
              slab_height = wheight - i - 1;
            }

            for (int j = world.m_start_width; j < world.m_end_width; j += world.m_slab_size)
            {
              if (j + slab_width > wwidth) {
                slab_width = wwidth - j - 1;
              }

              int w_center = wwidth / 2;
              int h_center = wheight / 2;

              std::shared_ptr<poly::structures::scene_slab> new_ti = std::make_shared<poly::structures::scene_slab>(
                world_ptr,
                storage_mutex,
                storage,
                j - w_center,
                j + slab_width - w_center,
                i - h_center,
                i + slab_height - h_center);

              // Add this slab to our pool
              slabs.push_back(new_ti);
            }
          }

          // Creat the specified number of threads and let them work on the pool of slabs
          std::cout << "INFO: rendering on " << num_threads << " threads" << std::endl;
          for (unsigned int i = 0; i < num_threads; i++) {
            thread_list.push_back(std::thread(
              [this, slablist_mutex, &slabs]
              {
                  std::shared_ptr<poly::structures::scene_slab> slab_ptr = nullptr;
                  size_t full_size = slabs.size();
                  while (true) {
                    { // sanity check scope for the mutex
                      const std::lock_guard<std::mutex> lock(*slablist_mutex);
                      if (slabs.empty()) {
                        break;
                      }
                      slab_ptr = slabs.back();
                      slabs.pop_back();
                      std::cout << "\r                                         ";
                      std::cout << "\rLOADING: " << ((float)slabs.size() * 100.0f/ full_size) << "% to go. " << slabs.size() << " slabs left";
                    }
                    this->render_slab(slab_ptr);
                  }
              })
            );
          }


          // Join all the threads
          for (std::thread& thread : thread_list) {
            if (thread.joinable())
            {
              thread.join();
            }
          }

          // reformat the 2D vector into a single dimensional array
          for (auto row : *(storage)) {
            for (auto el : row)
            {
              world.m_image.push_back(el);
            }
          }
        }

        void render_scene(poly::structures::World& world) const
        {
          int wheight = (int)world.m_vp->vres;
          int wwidth = (int)world.m_vp->hres;

          for (int i = (wheight / 2) - 1; i >= -(wheight / 2); i--){
            for (int j = -(wwidth / 2); j < (wwidth / 2); j++){

              Colour average = Colour(0.0f, 0.0f, 0.0f);
              unsigned int count = 0;

              int max_num_samples = world.m_sampler->num_samples_get();

              // For anti-aliasing
              for (int s = 0; s < max_num_samples; s++) {
                poly::structures::ShadeRec sr = poly::structures::ShadeRec(world);
                sr.m_colour = world.m_background;

                std::vector<float> sample =
                  world.m_sampler->sample_unit_square();

                atlas::math::Vector x = m_u * ((float)j
                                               + (float)sample.at(0));
                atlas::math::Vector y = m_v * ((float)i
                                               + (float)sample.at(1));
                atlas::math::Vector z = -m_w * (float)m_d;

                atlas::math::Vector direction =
                  glm::normalize((x + y + z));

                atlas::math::Ray<atlas::math::Vector> ray(m_eye,
                                                          direction);

                for (std::shared_ptr<poly::object::Object> obj : world.m_scene)
                {
                  obj->hit(ray, sr);
                }

                if (sr.m_material)
                {
                  average += sr.m_material->shade(sr);
                }
                else {
                  average += sr.m_colour;
                }
                count++;
              }

              world.m_image.push_back(colour_validate(average * (1.0f / (float)count))
              );
            }
            std::cout << "\r                                         ";
            std::cout << "\rLOADING: " << i + (wheight / 2) << " rows left";
          }
        }

    protected:
        void render_slab(std::shared_ptr<poly::structures::scene_slab> slab) const
        {
          poly::structures::World world = *(slab->world);
          std::shared_ptr<std::mutex> storage_mutex = slab->storage_mutex;
          std::shared_ptr<std::vector<std::vector<Colour>>> storage = slab->storage;

          int start_x = slab->start_x;
          int end_x = slab->end_x;
          int start_y = slab->start_y;
          int end_y = slab->end_y;

          std::vector<std::vector<Colour>> temp_storage = std::vector<std::vector<Colour>>(world.m_slab_size, std::vector<Colour>(world.m_slab_size));

          for (int i = start_y; i < end_y; i++)
          {
            for (int j = start_x; j < end_x; j++)
            {
              Colour average = Colour(0.0f, 0.0f, 0.0f);
              unsigned int count = 0;
              int max_num_samples = world.m_sampler->num_samples_get();

              // For anti-aliasing
              for (int s = 0; s < max_num_samples; s++) {
                poly::structures::ShadeRec sr = poly::structures::ShadeRec(world);
                sr.m_colour = world.m_background;
                sr.depth = 0;

                // Get the sample offsets [0, 1)
                std::vector<float> sample =
                  world.m_sampler->sample_unit_square(s);

                math::Vector x = m_u * ((float)j
                                        + (float)sample.at(0));
                math::Vector y = m_v * ((float)i
                                        + (float)sample.at(1));
                math::Vector z = -m_w * (float)m_d;

                math::Vector direction =
                  glm::normalize((x + y + z));

                math::Ray<math::Vector> ray(m_eye, direction);

                bool hit = false;
                for (std::shared_ptr<poly::object::Object> obj : world.m_scene) {
                  if (obj->hit(ray, sr)) {
                    hit = true;
                  }
                }

                // If we hit an object, it will have set the material
                if (hit && sr.m_material)
                {
                  average += sr.m_material->shade(sr);
                }
                else {
                  average += sr.m_colour;
                }
                count++;
              }

              int row_0_indexed = (int)i - start_y;
              int col_0_indexed = (int)j - start_x;

              temp_storage.at(row_0_indexed).at(col_0_indexed) = colour_validate(average * (1 / (float)count));
            }
          }


          for (int i = start_y; i < end_y; i++)
          {
            const std::lock_guard<std::mutex> lock(*storage_mutex);
            for (int j = start_x; j < end_x; j++) {

              //// 0,0 is in the center of the screen
              int row = (int)i + (int)(world.m_vp->vres / 2);
              int col = (int)j + (int)(world.m_vp->hres / 2);

              // Align the temp slab with the overall scene
              int row_0_indexed = (int)i - start_y;
              int col_0_indexed = (int)j - start_x;

              // Copy out info to the final storage location
              storage->at(world.m_vp->vres - row - 1).at(col) = temp_storage.at(row_0_indexed).at(col_0_indexed);

            }
          }

        }
    };
}
