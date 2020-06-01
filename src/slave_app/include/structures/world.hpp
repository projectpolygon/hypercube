#pragma once

namespace poly::light {class Light;}

#include <samplers/sampler.hpp>
#include "view_plane.hpp"
#include "tracers/tracer.hpp"
#include <objects/object.hpp>

namespace poly::structures {

    class World {
    public:
        Colour m_background{}; // Default pixel colour

        int m_start_width, m_start_height, m_end_width, m_end_height;

        std::shared_ptr<poly::sampler::Sampler> m_sampler; // The sampler for AA

        std::vector<std::shared_ptr<poly::object::Object>> m_scene; // Objects in our scene

        std::shared_ptr<poly::light::Light> m_ambient; // Ambient light in our scene (gets handled specially)
        std::vector<std::shared_ptr<poly::light::Light>> m_lights; // Lights in our scene
        std::vector<Colour> m_image; // Output as 1D array

        std::shared_ptr<ViewPlane> m_vp;

        std::shared_ptr<Tracer> m_tracer;

        unsigned int m_slab_size{};

        World() = default;
        ~World() = default;

    };
}
