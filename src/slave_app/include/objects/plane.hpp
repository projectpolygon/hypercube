#pragma once

#include <objects/object.hpp>

namespace poly::object {

    class Plane : public Object {

    public:

        Plane(math::Vector normal, math::Vector position)
        {
          this->normal = glm::normalize(normal);
          this->position = position;

          if (this->normal == math::Vector(0.0f, 1.0f, 0.0f)) {
            // Create the bounds
            bounds = Bounds3D(
              math::Vector(
                -std::numeric_limits<float>::max(),
                this->position.y - m_epsilon,
                -std::numeric_limits<float>::max()),
              math::Vector(
                std::numeric_limits<float>::max(),
                this->position.y + m_epsilon,
                std::numeric_limits<float>::max()));
          }
          else {
            // Create the bounds
            bounds = Bounds3D(
              math::Vector(
                std::numeric_limits<float>::min(),
                std::numeric_limits<float>::min(),
                std::numeric_limits<float>::min()),
              math::Vector(
                std::numeric_limits<float>::max(),
                std::numeric_limits<float>::max(),
                std::numeric_limits<float>::max()));
          }


        }

        bool closest_intersect_get(math::Ray<math::Vector>const& R,
                                   float& t_min) const
        {
          float d = glm::dot(this->normal, this->position);
          float num = d - glm::dot(this->normal, R.o);
          float den = glm::dot(this->normal, R.d);

          if (den < m_epsilon && den > -m_epsilon) {
            return false;
          }

          t_min = ((float)num / den);

          if (t_min > 0.0) {
            return true;
          }
          else {
            return false;
          }
        }

        bool hit(math::Ray<math::Vector>const& R,
                 ShadeRec& sr) const
        {
          float t{ std::numeric_limits<float>::max() };
          bool intersect = this->closest_intersect_get(R, t);

          // If this object is hit, set the shaderec with the relevant material and information about the hit point
          if (intersect && t < sr.m_tmin) {
            sr.m_normal = normal; // Override
            sr.m_ray = R;
            sr.m_tmin = t;
            sr.m_material = m_material;
          }

          return intersect;
        }

        bool shadow_hit([[maybe_unused]]math::Ray<math::Vector>const& R,
                        [[maybe_unused]]float& t) const
        {
          // Plane doesn't need to cast shadows or occlude
          return false;
        }

    private:
        math::Vector normal;
        math::Vector position;
    };
}
