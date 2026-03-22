
// You can write more code here

/* START OF COMPILED CODE */

/* START-USER-IMPORTS */
import Level from "./Level";
/* END-USER-IMPORTS */

export default class Pause extends Phaser.Scene {

	constructor() {
		super("Pause");

		/* START-USER-CTR-CODE */
		// Write your code here.
		/* END-USER-CTR-CODE */
	}

	editorCreate(): void {

		// background_color_trees
		this.add.image(106, 744, "background_color_trees");

		// background_fade_hills
		const background_fade_hills = this.add.image(106, 245, "background_fade_hills");
		background_fade_hills.flipY = true;

		// background_color_trees_1
		this.add.image(618, 744, "background_color_trees");

		// background_fade_hills_1
		const background_fade_hills_1 = this.add.image(618, 245, "background_fade_hills");
		background_fade_hills_1.flipY = true;

		// background_color_trees_2
		this.add.image(1129, 744, "background_color_trees");

		// background_fade_hills_2
		const background_fade_hills_2 = this.add.image(1129, 245, "background_fade_hills");
		background_fade_hills_2.flipY = true;

		// text_1
		const text_1 = this.add.text(432, 101, "", {});
		text_1.text = "Paused!";
		text_1.setStyle({ "fontSize": "100px", "fontStyle": "bold", "stroke": "#000000ff", "strokeThickness": 8 });

		// hill_top_smile
		const hill_top_smile = this.add.image(1219, 207, "hill_top_smile");
		hill_top_smile.angle = -90;

		// hud_player_yellow
		this.add.image(73, 76, "hud_player_yellow");

		// sign_exit
		this.add.image(770, 647, "sign_exit");

		// grass
		this.add.image(892, 643, "grass");

		// rock
		this.add.image(147, 746, "rock");

		// terrain_grass_block
		this.add.image(142, 870, "terrain_grass_block");

		// terrain_grass_horizontal_middle
		this.add.image(773, 770, "terrain_grass_horizontal_middle");

		// terrain_grass_horizontal_right
		this.add.image(901, 770, "terrain_grass_horizontal_right");

		// terrain_grass_horizontal_left
		this.add.image(646, 770, "terrain_grass_horizontal_left");

		// settings
		this.add.image(1200, 80, "gear");

		// terrain_grass_block_1
		this.add.image(444, 538, "terrain_grass_block");

		// continue_sign
		const continue_sign = this.add.image(440, 417, "continue");
		continue_sign.scaleX = 0.06;
		continue_sign.scaleY = 0.06;

		// cactus
		this.add.image(1201, 460, "cactus");

		// terrain_grass_horizontal_left_1
		this.add.image(1222, 584, "terrain_grass_horizontal_left");

		this.events.emit("scene-awake");
	}

	/* START-USER-CODE */

	// Write your code here

	create() {
		this.editorCreate();

		this.input.keyboard!.on('keydown-ESC', () => {
			this.scene.stop();
			this.scene.resume('Level');
		});

		const home = this.children.list.find(
			(child) => child instanceof Phaser.GameObjects.Image && child.texture.key === "sign_exit"
		) as Phaser.GameObjects.Image;

		home.setInteractive({ useHandCursor: true });
		home.on("pointerdown", () => {
			const levelScene = this.scene.get("Level") as Level;
			levelScene.sendQuitTelemetry().finally(() => {
				window.location.href = "https://bachelor.openpace.org";
			});
		});

		const resumeHandler = () => {
			this.scene.stop();
			this.scene.resume('Level');
		};

		for (const child of this.children.list) {
			if (child instanceof Phaser.GameObjects.Image &&
				(child.texture.key === "gear" || child.texture.key === "continue")) {
				child.setInteractive({ useHandCursor: true });
				child.on("pointerdown", resumeHandler);
			}
		}
	}

	/* END-USER-CODE */
}

/* END OF COMPILED CODE */

// You can write more code here
