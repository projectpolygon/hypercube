#pragma once

namespace poly::light {

    class PointLight : public Light
    {
    public:

        PointLight() : Light()
        {
          m_location = atlas::math::Vector(0.0f, 0.0f, 0.0f);
        }

        PointLight(math::Vector const& location) : Light()
        {
          m_location = location;
        }

        void location_set(atlas::math::Point const& location)
        {
          m_location = glm::normalize(location);
        }

        atlas::math::Vector direction_get(poly::structures::ShadeRec& sr)
        {
          math::Vector surface_point = sr.hitpoint_get();
          return glm::normalize(m_location - surface_point);
        }

        bool in_shadow(math::Ray<math::Vector> const& shadow_ray,
                       poly::structures::ShadeRec const& sr)
        {
          float t{std::numeric_limits<float>::max()};

          // Max distance between hitpoint and light
          math::Vector line_between = m_location - shadow_ray.o;
          float line_distance = sqrt(glm::dot(line_between, line_between));

          for (std::shared_ptr<poly::object::Object> object : sr.m_world.m_scene) {
            // If we hit an object with distance less than max
            if (object->shadow_hit(shadow_ray, t) && t < line_distance) {
              return true;
            }
          }

          return false;
        }

        Colour L(poly::structures::ShadeRec& sr)
        {
          math::Point new_origin = sr.hitpoint_get();
          math::Vector new_direction = glm::normalize(direction_get(sr));

          math::Ray shadow_ray(new_origin
                               + (m_surface_epsilon
                                  * new_direction),
                               new_direction);
          if (in_shadow(shadow_ray, sr)) {
            return Colour(0.0f, 0.0f, 0.0f);
          }
          else {
            math::Vector vector = glm::normalize(m_location
                                                 - sr.hitpoint_get());
            float r_squared = glm::dot(vector, vector);
            return m_colour * m_ls / (r_squared);
          }
        }

    protected:
        atlas::math::Point m_location;
    };

}