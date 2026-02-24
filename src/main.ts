import Phaser from "phaser";
import Level from "./scenes/Level";
import Preload from "./scenes/Preload";
import Pause from "./scenes/Pause";
import Start from "./scenes/Start";
import Finish from "./scenes/Finish";

class Boot extends Phaser.Scene {

	constructor() {
		super("Boot");
	}

	preload() {

		this.load.pack("pack", "assets/preload-asset-pack.json");
		this.load.image("buttonStart", "assets/game_icons_double/buttonStart.png");
	}

	create() {

		this.scene.start("Start");
	}
}

window.addEventListener('load', function () {

	const game = new Phaser.Game({
		width: 1280,
		height: 1000,
		backgroundColor: "#2f2f2f",
		parent: "game-container",
		scale: {
			mode: Phaser.Scale.ScaleModes.HEIGHT_CONTROLS_WIDTH,
			autoCenter: Phaser.Scale.Center.CENTER_BOTH
		},
		scene: [Boot, Preload, Level, Pause, Start, Finish],
		physics: {
			default: 'arcade',
			arcade: {
				debug: false,
				gravity: {
					x: 0, y: 2000
				},
			}
		}
	});

	game.scene.start("Boot");
});