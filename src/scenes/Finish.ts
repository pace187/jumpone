
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

		// background_solid_grass
		const background_solid_grass = this.add.tileSprite(0, 0, 1280, 1000, "background_solid_grass");
		background_solid_grass.setOrigin(0, 0);

		// star
		const star = this.add.image(669, 198, "star");
		star.scaleX = 2;
		star.scaleY = 2;

		// text_1
		const text_1 = this.add.text(440, 385, "", {});
		text_1.text = "You Won!";
		text_1.setStyle({ "fontSize": "100px", "fontStyle": "bold" });

		// home
		const home = this.add.image(660, 780, "home");
		home.scaleX = 2;
		home.scaleY = 2;

		this.events.emit("scene-awake");
	}

	/* START-USER-CODE */

	// Write your code here

	create() {

		this.editorCreate();

		const home = this.children.list.find(
			(child) => child instanceof Phaser.GameObjects.Image && child.texture.key === "home"
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
