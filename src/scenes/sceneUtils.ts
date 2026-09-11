// small helpers shared by the scenes. phaser editor owns the generated scene
// files, so hand-written code that more than one scene needs lives here.

/** first image in the display list using the given texture. editor-created
 *  objects are not exposed as fields, so they are looked up by texture key. */
export function findImageByTexture(scene: Phaser.Scene, textureKey: string): Phaser.GameObjects.Image {
	return scene.children.list.find(
		(child) => child instanceof Phaser.GameObjects.Image && child.texture.key === textureKey
	) as Phaser.GameObjects.Image;
}

/** every image in the display list using one of the given textures. */
export function findImagesByTexture(scene: Phaser.Scene, ...textureKeys: string[]): Phaser.GameObjects.Image[] {
	return scene.children.list.filter(
		(child): child is Phaser.GameObjects.Image =>
			child instanceof Phaser.GameObjects.Image && textureKeys.includes(child.texture.key)
	);
}
