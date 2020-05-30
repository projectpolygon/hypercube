#pragma once

#include <memory>
#include "types/atlas_types.hpp"

namespace poly::material {class Material;}

namespace poly::structures {

    class World;


    class ShadeRec {
    public:
        float m_tmin;
        float u, v;
        unsigned int depth;
        atlas::math::Ray<atlas::math::Vector> m_ray;
        World& m_world;
        std::shared_ptr<poly::material::Material> m_material;
        Colour m_colour;
        atlas::math::Normal m_normal;

        ShadeRec(World& world)
          : m_world(world), m_material{nullptr},
            m_colour{ Colour(0.0f, 0.0f, 0.0f) },
            m_normal{math::Vector(0.0f, 0.0f, 0.0f)}
        {
          m_tmin = std::numeric_limits<float>::max();
          depth = 0;
        }

        math::Vector hitpoint_get() const
        {
          return m_ray.o + m_ray.d * m_tmin;
        }
    };


}