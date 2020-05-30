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

	srand((unsigned int) time(0));

	nlohmann::json task = poly::utils::open_json_file(argv[1]);
	poly::structures::World w2 = poly::utils::create_world(task);
	poly::camera::PinholeCamera cam2 = poly::utils::parse_camera(task["camera"]);

  std::shared_ptr<poly::structures::ViewPlane> vp = std::make_shared<poly::structures::ViewPlane>();

  vp->hres = 1000;
  vp->vres = 1000;
  vp->max_depth = 5;

  poly::structures::World w = poly::structures::World();
  w.m_vp = vp;
  w.m_background = {0.0f, 0.0f, 0.0f};
  w.m_sampler = std::make_shared<poly::sampler::AA_Jittered>(9, 1);
  w.m_slab_size = 1000;
  w.m_tracer = std::make_shared<poly::structures::WhittedTracer>(&w);

  std::vector<std::shared_ptr<poly::object::Object>> scene;
  w.m_scene = scene;

  std::shared_ptr<poly::object::Sphere> sphere = std::make_shared<poly::object::Sphere>(
    math::Vector(0.0f, -0.0f, 150.0f), 30.0f);
  sphere->material_set(std::make_shared<poly::material::Matte>(0.5f, Colour{0.0f, 0.0f, 1.0f}));
  w.m_scene.push_back(sphere);

  std::shared_ptr<poly::light::PointLight> ptlt = std::make_shared<poly::light::PointLight>(
    math::Vector(0.0f, 100.0f, 150.0f));
  ptlt->radiance_scale(5.0f);
  w.m_lights.push_back(ptlt);

	std::shared_ptr<poly::light::AmbientLight> amb = std::make_shared<poly::light::AmbientLight>();
	amb->colour_set(Colour(1.0f, 1.0f, 1.0f));
	amb->radiance_scale(0.3f);
	w.m_ambient = amb;

  poly::camera::PinholeCamera cam = poly::camera::PinholeCamera(400.0f);
  cam.eye_set(atlas::math::Point(0.0f, 60.0f, 300.0f));
  cam.lookat_set(atlas::math::Point(0.0f, 0.0f, 0.0f));
  cam.upvec_set(atlas::math::Vector(0.0f, 1.0f, 0.0f));
  cam.uvw_compute();

	cam2.multithread_render_scene(w2, task["threads"]);

	saveToBMP("render.bmp", w2.m_start_width, w2.m_end_width, w2.m_start_height, w2.m_end_height, w2.m_image);

  return 0;
}



/**
 * Saves a BMP image file based on the given array of pixels. All pixel values
 * have to be in the range [0, 1].
 *
 * @param filename The name of the file to save to.
 * @param start_width The start width of the image.
 * @param end_width The end width of the image.
 * @param start_height The start height of the image.
 * @param start_height The end height of the image.
 * @param image The array of pixels representing the image.
 */
void saveToBMP(std::string const& filename,
							 std::size_t start_width,
							 std::size_t end_width,
							 std::size_t start_height,
							 std::size_t end_height,
							 std::vector<Colour> const& image)
{
	std::vector<unsigned char> data(image.size() * 3);
	std::size_t width = end_width - start_width;
	std::size_t height = end_height - start_height;

	for (std::size_t i{start_height}, k{0}; i < end_height; ++i)
	{
		for (std::size_t j{start_width}; j < end_width; ++j, k += 3) {
			Colour pixel = image[(i * width) + j];
			data[k + 0]  = static_cast<unsigned char>(pixel.r * 255);
			data[k + 1]  = static_cast<unsigned char>(pixel.g * 255);
			data[k + 2]  = static_cast<unsigned char>(pixel.b * 255);
		}
	}

	std::cout << std::endl << data.size() << std::endl;
	std::cout << end_height << std::endl;

	stbi_write_bmp(filename.c_str(),
								 static_cast<int>(width),
								 static_cast<int>(height),
								 3,
								 data.data());
}

