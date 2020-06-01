//
// Created by duncan on 2020-05-29.
//
#include <memory>

#include "structures/world.hpp"
#include "objects/sphere.hpp"
#include "materials/matte.hpp"
#include "cameras/pinhole.hpp"
#include "samplers/jittered.hpp"
#include "structures/view_plane.hpp"
#include "tracers/whitted_tracer.hpp"
#include "lights/point_light.hpp"
#include "lights/ambient.hpp"
#include "utils/parser.hpp"
#include "paths.hpp"

int main([[maybe_unused]] int argc, [[maybe_unused]] char** argv) {

	if (argc <= 1) {
		std::wcerr << "Need file path" << std::endl;
		exit(1);
	}

	srand((unsigned int) time(0));

	nlohmann::json task = poly::utils::open_json_file(argv[1]);
	poly::structures::World w = poly::utils::create_world(task);
	poly::camera::PinholeCamera cam = poly::utils::parse_camera(task["camera"]);

	cam.multithread_render_scene(w, task["max_threads"]);

	std::cout << ShaderPath << std::endl;

	std::string out_file = task["output_file"];
	saveToBMP(ShaderPath + out_file, w);

  return 0;
}



/**
 * Saves a BMP image file based on the given array of pixels. All pixel values
 * have to be in the range [0, 1].
 *
 * @param filename The name of the file to save to.
 * @param w The world object is used for the dimension used to
 * create the graphic
 */
void saveToBMP(std::string const& filename,
							 poly::structures::World& w)
{
	std::vector<unsigned char> data(w.m_image.size() * 3);
	int width = w.m_vp->vres;
	int height = w.m_vp->hres;

	for (int i{height - w.m_end_height}, k{0}; i < height - w.m_start_height; ++i)
	{
		for (int j{w.m_start_width}; j < w.m_end_width; ++j, k += 3) {
			Colour pixel = w.m_image[(i * width) + j];
			data[k + 0]  = static_cast<unsigned char>(pixel.r * 255);
			data[k + 1]  = static_cast<unsigned char>(pixel.g * 255);
			data[k + 2]  = static_cast<unsigned char>(pixel.b * 255);
		}
	}

	stbi_write_bmp(filename.c_str(),
								 static_cast<int>(w.m_end_width - w.m_start_width),
								 static_cast<int>(w.m_end_height - w.m_start_height),
								 3,
								 data.data());
}

