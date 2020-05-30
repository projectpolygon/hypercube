#pragma once

#include <types/atlas_types.hpp>
#include "world.hpp"

namespace poly::structures {

    class scene_slab {
    public:
        std::shared_ptr<World> world;
        std::shared_ptr<std::mutex> storage_mutex;
        std::shared_ptr<std::vector<std::vector<Colour>>> storage;
        int start_x;
        int end_x;
        int start_y;
        int end_y;

        scene_slab(
          std::shared_ptr<World> _world,
          std::shared_ptr<std::mutex> _storage_mutex,
          std::shared_ptr<std::vector<std::vector<Colour>>> _storage,
          int _start_x,
          int _end_x,
          int _start_y,
          int _end_y)
        {
          world = _world;
          storage_mutex = _storage_mutex;
          storage = _storage;
          start_x = _start_x;
          end_x = _end_x;
          start_y = _start_y;
          end_y = _end_y;
        }


    };
}