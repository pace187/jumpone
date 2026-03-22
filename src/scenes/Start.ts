
// You can write more code here

/* START OF COMPILED CODE */

/* START-USER-IMPORTS */
/* END-USER-IMPORTS */

export default class Start extends Phaser.Scene {

	constructor() {
		super("Start");

		/* START-USER-CTR-CODE */
		// Write your code here.
		/* END-USER-CTR-CODE */
	}

	editorCreate(): void {

		// background_fade_trees
		this.add.image(-296, 747, "background_fade_trees");

		// background_fade_hills
		const background_fade_hills = this.add.image(-296, 247, "background_fade_hills");
		background_fade_hills.flipY = true;

		// background_fade_trees_1
		this.add.image(200, 747, "background_fade_trees");

		// background_fade_hills_1
		const background_fade_hills_1 = this.add.image(200, 247, "background_fade_hills");
		background_fade_hills_1.flipY = true;

		// background_fade_trees_2
		this.add.image(709, 747, "background_fade_trees");

		// background_fade_hills_2
		const background_fade_hills_2 = this.add.image(709, 247, "background_fade_hills");
		background_fade_hills_2.flipY = true;

		// background_fade_trees_3
		this.add.image(1205, 747, "background_fade_trees");

		// background_fade_hills_3
		const background_fade_hills_3 = this.add.image(1205, 247, "background_fade_hills");
		background_fade_hills_3.flipY = true;

		// buttonStart
		const buttonStart = this.add.image(640, 600, "buttonStart");
		buttonStart.tintTopLeft = 377874;
		buttonStart.tintBottomRight = 0;

		// movementExplanation
		const movementExplanation = this.add.text(139, 102, "", {});
		movementExplanation.text = "hold SPACEBAR to charge your Jump\n\n\nLeftKey/RightKey: Go Left/Go Right\n\n\nESC:              Pause";
		movementExplanation.setStyle({ "color": "#000000ff", "fontSize": "50px", "fontStyle": "bold" });

		// bush
		this.add.image(268, 941, "bush");

		// cactus
		this.add.image(1077, 945, "cactus");

		// mushroom_red
		this.add.image(1151, 355, "mushroom_red");

		// terrain_grass_block
		this.add.image(1150, 479, "terrain_grass_block");

		// hill_top_smile
		this.add.image(265, 576, "hill_top_smile");

		// terrain_grass_horizontal_overhang_left
		this.add.image(201, 701, "terrain_grass_horizontal_overhang_left");

		// terrain_grass_horizontal_overhang_right
		this.add.image(328, 701, "terrain_grass_horizontal_overhang_right");

		// hud_player_yellow
		this.add.image(78, 78, "hud_player_yellow");

		this.events.emit("scene-awake");
	}

	/* START-USER-CODE */

	// Write your code here

	create() {

		this.editorCreate();

		const buttonStart = this.children.list.find(
			(child) => child instanceof Phaser.GameObjects.Image && child.texture.key === "buttonStart"
		) as Phaser.GameObjects.Image;

		buttonStart.setInteractive({ useHandCursor: true });
		buttonStart.on("pointerdown", () => {
			this.scene.start("Preload");
		});
	}

	/* END-USER-CODE */
}

/* END OF COMPILED CODE */

// You can write more code here
