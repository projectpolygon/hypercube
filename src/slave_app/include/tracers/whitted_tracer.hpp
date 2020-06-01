#pragma once

#include <structures/world.hpp>

namespace poly::structures {

    class WhittedTracer : public Tracer {
    public:
        WhittedTracer(poly::structures::World* _world) :Tracer(_world) {}

        Colour trace_ray(math::Ray<math::Vector> const& ray, const unsigned int depth) const
        {
          if (depth > m_world->m_vp->max_depth) {
            return Colour(0.0f, 0.0f, 0.0f);
          }
          else {
            poly::structures::ShadeRec temp_sr = poly::structures::ShadeRec(*(m_world));
            bool did_hit = false;
            for (auto obj : m_world->m_scene) {
              if (obj->hit(ray, temp_sr)) {
                did_hit = true;
              }
            }

            // If this ray hit an object, return material's shading
            if (did_hit && temp_sr.m_material != nullptr) {
              temp_sr.depth = depth;
              temp_sr.m_ray = ray;
              return temp_sr.m_material->shade(temp_sr);
            }
            else {
              return m_world->m_background;
            }
          }
        }
    };
}