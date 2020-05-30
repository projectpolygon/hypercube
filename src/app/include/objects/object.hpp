#pragma once

#include <materials/material.hpp>
#include <structures/bounds.hpp>
#include <structures/shade_rec.hpp>
#include <memory>

namespace poly::object {

    class Object {
    public:
        std::shared_ptr<poly::material::Material> m_material;

        Object()
        {
          m_epsilon = 0.001f;
        }
        virtual bool hit(math::Ray<math::Vector>const& R, poly::structures::ShadeRec& sr) const = 0;
        virtual bool shadow_hit(math::Ray<math::Vector>const& R, float& t) const = 0;

        virtual poly::structures::Bounds3D boundbox_get() const
        {
          return bounds;
        }

        void material_set(std::shared_ptr<poly::material::Material> const& material)
        {
          m_material = material;
        }
        std::shared_ptr<poly::material::Material> material_get() const
        {
          return m_material;
        }

    protected:
        float m_epsilon;
        poly::structures::Bounds3D bounds;
    };
}