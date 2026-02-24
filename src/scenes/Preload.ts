
// You can write more code here

/* START OF COMPILED CODE */

/* START-USER-IMPORTS */
/* END-USER-IMPORTS */

export default class Preload extends Phaser.Scene {

	constructor() {
		super("Preload");

		/* START-USER-CTR-CODE */
		// Write your code here.
		/* END-USER-CTR-CODE */
	}

	editorCreate(): void {

		// background_clouds
		this.add.tileSprite(671, 345, 2048, 512, "background_clouds");

		// background_solid_cloud
		this.add.tileSprite(669, 827, 2048, 500, "background_solid_cloud");

		// background_solid_sky
		this.add.tileSprite(671, -2, 2048, 256, "background_solid_sky");

		// guapen
		this.add.image(516, 522, "hud_player_yellow");

		// progressBar
		const progressBar = this.add.rectangle(589, 528, 256, 20);
		progressBar.setOrigin(0, 0);
		progressBar.isFilled = true;
		progressBar.fillColor = 14737632;

		// progressBarBg
		const progressBarBg = this.add.rectangle(589, 528, 256, 20);
		progressBarBg.setOrigin(0, 0);
		progressBarBg.isStroked = true;

		// loadingText
		const loadingText = this.add.text(588, 496, "", {});
		loadingText.text = "Loading...";
		loadingText.setStyle({ "color": "#ffffffff", "fontFamily": "arial", "fontSize": "20px", "stroke": "#000000ff", "strokeThickness": 2 });

		this.progressBar = progressBar;

		this.events.emit("scene-awake");
	}

	private progressBar!: Phaser.GameObjects.Rectangle;

	/* START-USER-CODE */

	// Write your code here

	preload() {

		this.editorCreate();

		this.load.pack("asset-pack", "assets/asset-pack.json");

		const width = this.progressBar.width;

		this.load.on("progress", (value: number) => {

			this.progressBar.width = width * value;
		});
	}

	create() {

		if (process.env.NODE_ENV === "development") {

			const start = new URLSearchParams(location.search).get("start");

			if (start) {

				console.log(`Development: jump to ${start}`);
				this.scene.start(start);

				return;
			}
		}

		this.scene.start("Level");
	}

	/* END-USER-CODE */
}

/* END OF COMPILED CODE */

// You can write more code here
