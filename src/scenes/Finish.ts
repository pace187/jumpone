
// You can write more code here

/* START OF COMPILED CODE */

/* START-USER-IMPORTS */
/* END-USER-IMPORTS */

export default class Finish extends Phaser.Scene {

	constructor() {
		super("Finish");

		/* START-USER-CTR-CODE */
		// Write your code here.
		/* END-USER-CTR-CODE */
	}

	editorCreate(): void {

		// background_color_trees
		this.add.image(110, 749, "background_color_trees");

		// background_fade_hills
		const background_fade_hills = this.add.image(110, 250, "background_fade_hills");
		background_fade_hills.flipY = true;

		// background_color_trees_1
		this.add.image(622, 749, "background_color_trees");

		// background_fade_hills_1
		const background_fade_hills_1 = this.add.image(622, 250, "background_fade_hills");
		background_fade_hills_1.flipY = true;

		// background_color_trees_2
		this.add.image(1133, 749, "background_color_trees");

		// background_fade_hills_2
		const background_fade_hills_2 = this.add.image(1133, 250, "background_fade_hills");
		background_fade_hills_2.flipY = true;

		// star
		this.add.image(674, 257, "star");

		// text_1
		const text_1 = this.add.text(440, 385, "", {});
		text_1.text = "You Won!";
		text_1.setStyle({ "fontSize": "100px", "fontStyle": "bold", "stroke": "#000000ff", "strokeThickness": 8 });

		// hill_top_smile
		const hill_top_smile = this.add.image(1223, 212, "hill_top_smile");
		hill_top_smile.angle = -90;

		// hud_player_yellow
		this.add.image(77, 81, "hud_player_yellow");

		// sign_exit
		this.add.image(672, 608, "sign_exit");

		// grass
		this.add.image(803, 608, "grass");

		// rock
		this.add.image(244, 719, "rock");

		// terrain_grass_block
		this.add.image(239, 843, "terrain_grass_block");

		// terrain_grass_horizontal_middle
		this.add.image(675, 731, "terrain_grass_horizontal_middle");

		// terrain_grass_horizontal_right
		this.add.image(803, 731, "terrain_grass_horizontal_right");

		// terrain_grass_horizontal_left
		this.add.image(548, 731, "terrain_grass_horizontal_left");

		this.events.emit("scene-awake");
	}

	/* START-USER-CODE */

	// Write your code here

	create() {

		this.editorCreate();

		const home = this.children.list.find(
			(child) => child instanceof Phaser.GameObjects.Image && child.texture.key === "sign_exit"
		) as Phaser.GameObjects.Image;

		home.setInteractive({ useHandCursor: true });
		home.on("pointerdown", () => {
			window.location.href = "https://bachelor.openpace.org/";
		});
	}

	/* END-USER-CODE */
}

/* END OF COMPILED CODE */

// You can write more code here
