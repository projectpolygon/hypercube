#pragma once

namespace poly::object {

    class Sphere : public Object {
    public:
        Sphere(math::Vector position, float radius)
        {
          this->r = radius;
          this->C = position;

          // Create the bounds
          bounds = poly::structures::Bounds3D(
            math::Vector(
              position.x - r,
              position.y - r,
              position.z - r),
            math::Vector(
              position.x + r,
              position.y + r,
              position.z + r));
        }

        poly::structures::Bounds3D boundbox_get() const
        {
          return bounds;
        };

        math::Vector normal_get(math::Ray<math::Vector>const& R,
                                float t) const
        {
          math::Vector point = R.o + t * R.d;
          return glm::normalize(point - C);
        }

        bool hit(math::Ray<math::Vector>const& R,
                 poly::structures::ShadeRec& sr) const
        {
          float t{ std::numeric_limits<float>::max() };
          bool intersect = this->closest_intersect_get(R, t);

          // If this object is hit, set the shaderec with the relevant material and information about the hit point
          if (intersect && t < sr.m_tmin) {
            sr.m_normal = normal_get(R, t);
            sr.m_ray = R;
            sr.m_tmin = t;
            sr.m_material = m_material;
          }

          return intersect;
        }

        bool shadow_hit(math::Ray<math::Vector>const& R,
                        float& t) const
        {
          float temp_t;
          if (this->closest_intersect_get(R, temp_t) && temp_t < t && temp_t > m_epsilon) {
            t = temp_t;
            return true;
          }
          return false;
          //return this->closest_intersect_get(R,t);
        }

        bool closest_intersect_get(const math::Ray<math::Vector>& R,
                                   float& t_min) const
        {
          float a = (float)glm::dot(R.d, R.d);
          float b = (float)2.0f * glm::dot(R.d, R.o - this->C);
          float c = (float)glm::dot(R.o - this->C, R.o - this->C)
                    - (float)(this->r * this->r);

          float disc = b * b - (4.0f * a * c);
          if (zeus::geq((float)disc, 0.0f)) {
            const float e = std::sqrt(disc);
            const float denom = 2.0f * a;

            const float eps = 0.1f;
            // Look at the negative root first
            float t = (-b - e) / denom;
            if (zeus::geq(t, eps))
            {
              t_min = t;
              return true;
            }

            // Now the positive root
            t = (-b + e) / denom;
            if (zeus::geq(t, eps))
            {
              t_min = t;
              return true;
            }
          }
          return false;
        }

    private:
        math::Vector C; // Center of the sphere
        double r; // Radius of the sphere
    };
}

