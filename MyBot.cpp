#include "MyBot.h"
#include <dpp/dpp.h>

std::string extractFirstValue(const std::string& filename) {
	std::ifstream file(filename);
	std::string line, value;

	if (file.is_open()) {
		if (std::getline(file, line)) {
			std::istringstream iss(line);
			std::string key;
			if (std::getline(iss, key, '=')) {
				std::getline(iss, value);
			}
		}
		file.close();
	}
	else {
		std::cerr << "Unable to open file " << filename << std::endl;
	}

	return value;
}

const std::string ENVFILE = "../.env";
const std::string BOT_TOKEN = extractFirstValue(ENVFILE);

int main()
{
	dpp::cluster bot(BOT_TOKEN, dpp::i_default_intents | dpp::i_message_content);

	bot.on_message_create([&bot](const dpp::message_create_t& event) {
		if (event.msg.content=="$test") {
			event.reply("yodie gangg spliffy gang", true);
		}
	});

	bot.on_ready([&bot](const dpp::ready_t& event) {
		if (dpp::run_once<struct register_bot_commands>()) {
			bot.global_command_create(dpp::slashcommand("ping", "init", bot.me.id));
		}
	});

	bot.start(dpp::st_wait);
	return 0;
}
