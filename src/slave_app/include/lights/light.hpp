#pragma once

#include <structures/shade_rec.hpp>
#include <structures/world.hpp>
#include <objects/object.hpp>

namespace poly::light {

    class Light {
    public:
        Light() : m_ls{ 1.0f }, m_colour{ 1.0f, 1.0f, 1.0f }, m_surface_epsilon{ 0.001f } {}
        virtual atlas::math::Vector direction_get(poly::structures::ShadeRec& sr) = 0;
        virtual Colour L(poly::structures::ShadeRec& sr) = 0;

        void radiance_scale(float b)
        {
          m_ls = b;
        }

        void colour_set(Colour const& c)
        {
          m_colour = c;
        }

    protected:

        float m_ls;
        Colour m_colour;
        float m_surface_epsilon;

        virtual bool in_shadow(math::Ray<math::Vector> const& shadow_ray,
                               poly::structures::ShadeRec const& sr)
        {
          float t;
          for (std::shared_ptr<poly::object::Object> object : sr.m_world.m_scene) {
            if (object->shadow_hit(shadow_ray, t) && t > m_surface_epsilon) {
              return true;
            }
          }
          return false;
        }
    };
}