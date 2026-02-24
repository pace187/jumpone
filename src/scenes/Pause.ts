
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

		// background_solid_sand
		const background_solid_sand = this.add.tileSprite(0, 0, 1280, 1000, "background_solid_sand");
		background_solid_sand.setOrigin(0, 0);

		// settings
		this.add.image(1200, 80, "gear");

		// home
		const home = this.add.image(654, 488, "home");
		home.scaleX = 2;
		home.scaleY = 2;

		// endRun
		const endRun = this.add.text(539, 558, "", {});
		endRun.text = "End Run!";
		endRun.setStyle({ "color": "#ff0404ff", "fontSize": "56px", "fontStyle": "bold" });

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
			(child) => child instanceof Phaser.GameObjects.Image && child.texture.key === "home"
		) as Phaser.GameObjects.Image;

		home.setInteractive({ useHandCursor: true });
		home.on("pointerdown", () => {
			const levelScene = this.scene.get("Level") as Level;

			fetch(`${levelScene["SUPABASE_URL"]}/rest/v1/telemetry`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"apikey": levelScene["SUPABASE_ANON_KEY"],
					"Authorization": `Bearer ${levelScene["SUPABASE_ANON_KEY"]}`,
					"Prefer": "return=minimal"
				},
				body: JSON.stringify({
					session_id: levelScene.sessionId,
					pos_x: levelScene.arcadesprite_1.x,
					pos_y: levelScene.arcadesprite_1.y,
					vel_x: 0,
					vel_y: 0,
					checkpointReached: levelScene.checkpointsReached,
					state: "Quit",
					timestamp: Date.now()
				})
			}).finally(() => {
				window.location.href = "index.html";
			});
		});

		const game = this.children.list.find(
			(child) => child instanceof Phaser.GameObjects.Image && child.texture.key === "gear"
		) as Phaser.GameObjects.Image;

		game.setInteractive({ useHandCursor: true });
		game.on("pointerdown", () => {
			this.scene.stop();
			this.scene.resume('Level');
		});
	}

	/* END-USER-CODE */
}

/* END OF COMPILED CODE */

// You can write more code here
