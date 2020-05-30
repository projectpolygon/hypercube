#pragma once

#include "types/atlas_types.hpp"

namespace poly::structures {
    class Bounds3D {
    public:

        math::Vector pMin;
        math::Vector pMax;

        Bounds3D()
        {
          pMin = math::Vector(0.0f, 0.0f, 0.0f);
          pMax = math::Vector(0.0f, 0.0f, 0.0f);
        }
        Bounds3D(math::Vector _pMin, math::Vector _pMax) : pMin{ _pMin }, pMax{ _pMax }{}

        inline bool get_intersects(const math::Ray<math::Vector>& ray, float* hitt0, float* hitt1) const
        {
          float t0 = 0;
          float t1 = std::numeric_limits<float>::max();
          for (int i = 0; i < 3; ++i) {
            float invRayDir = 1 / ray.d[i];
            float tNear = (pMin[i] - ray.o[i]) * invRayDir;
            float tFar = (pMax[i] - ray.o[i]) * invRayDir;
            if (tNear > tFar) {
              std::swap(tNear, tFar);
            }

            tFar *= 1.0f + 2.0f * (3.0f * (float)std::numeric_limits<float>::epsilon() * 0.5f)
                           / (1.0f - 3.0f * (float)std::numeric_limits<float>::epsilon() * 0.5f);

            t0 = tNear > t0 ? tNear : t0;
            t1 = tFar < t1 ? tFar : t1;
            if (t0 > t1) {
              return false;
            }

          }
          if (hitt0) {
            *hitt0 = t0;
          }
          if (hitt1) {
            *hitt1 = t1;
          }
          return true;
        }

        math::Vector diagonal() const
        {
          return pMax - pMin;
        }

        float surfaceArea() const
        {
          math::Vector d = diagonal();
          return 2 * (d.x * d.y + d.x * d.z + d.y * d.z);
        }

        int maximum_extent() const
        {
          math::Vector d = diagonal();
          if (d.x > d.y&& d.x > d.z)
            return 0;
          else if (d.y > d.z)
            return 1;
          else
            return 2;
        }

    private:
    };
}