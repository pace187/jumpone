
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

		// background_solid_sand
		const background_solid_sand = this.add.tileSprite(0, 0, 1280, 1000, "background_solid_sand");
		background_solid_sand.setOrigin(0, 0);

		// buttonStart
		const buttonStart = this.add.image(640, 697, "buttonStart");
		buttonStart.scaleX = 2;
		buttonStart.scaleY = 2;

		// movementExplanation
		const movementExplanation = this.add.text(147, 216, "", {});
		movementExplanation.text = "hold SPACEBAR to charge your Jump\n\nLeftKey/RightKey: Go Left/Go Right\n\nESC:              Pause";
		movementExplanation.setStyle({ "color": "#000000ff", "fontSize": "50px", "fontStyle": "bold" });

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
