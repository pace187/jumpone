// Small helpers shared by the scenes. Phaser Editor 2D owns the generated
// scene files, so anything hand-written that more than one scene needs lives here.

/**
 * First image in the scene's display list that uses the given texture.
 * Editor-created objects are not exposed as fields, so they are looked up by texture key.
 */
export function findImageByTexture(scene: Phaser.Scene, textureKey: string): Phaser.GameObjects.Image {
	return scene.children.list.find(
		(child) => child instanceof Phaser.GameObjects.Image && child.texture.key === textureKey
	) as Phaser.GameObjects.Image;
}

/** Every image in the scene's display list using one of the given textures. */
export function findImagesByTexture(scene: Phaser.Scene, ...textureKeys: string[]): Phaser.GameObjects.Image[] {
	return scene.children.list.filter(
		(child): child is Phaser.GameObjects.Image =>
			child instanceof Phaser.GameObjects.Image && textureKeys.includes(child.texture.key)
	);
}
