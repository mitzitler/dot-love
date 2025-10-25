import Phaser from 'phaser';
import { MILITSA_GAME_CONFIG, MILITSA_TEXT_STYLES } from './militsaGameConfig';

export function createMilitsaGameScene(onGameOver, firstName, lastName) {
  return {
    preload: function() {
      // Load background image from CDN
      this.load.image(
        MILITSA_GAME_CONFIG.backgroundImage.key,
        MILITSA_GAME_CONFIG.backgroundImage.url
      );

      // Load all 3 face images from CDN
      MILITSA_GAME_CONFIG.ballFaces.forEach(face => {
        this.load.image(face.key, face.url);
      });
    },

    create: function() {
      const scene = this;
      scene.score = 0;
      scene.gameOver = false;

      // Add background image (renders behind everything)
      scene.add.image(
        MILITSA_GAME_CONFIG.width / 2,
        MILITSA_GAME_CONFIG.height / 2,
        MILITSA_GAME_CONFIG.backgroundImage.key
      ).setDisplaySize(MILITSA_GAME_CONFIG.width, MILITSA_GAME_CONFIG.height);

      // Score text
      scene.scoreText = scene.add.text(
        MILITSA_GAME_CONFIG.width / 2,
        30,
        'Score: 0',
        MILITSA_TEXT_STYLES.score
      ).setOrigin(0.5);

      // Instructions
      scene.instructionText = scene.add.text(
        MILITSA_GAME_CONFIG.width / 2,
        65,
        'Click to keep it up!',
        MILITSA_TEXT_STYLES.instructions
      ).setOrigin(0.5);

      // Create ball sprite with first face
      scene.ball = scene.add.sprite(
        MILITSA_GAME_CONFIG.width / 2,
        200,
        MILITSA_GAME_CONFIG.ballFaces[0].key
      );
      scene.ball.setDisplaySize(MILITSA_GAME_CONFIG.ballDisplaySize, MILITSA_GAME_CONFIG.ballDisplaySize);
      scene.physics.add.existing(scene.ball);
      scene.ball.body.setBounce(0.3);
      scene.ball.body.setCollideWorldBounds(true);
      scene.ball.setInteractive();

      // Track current face index for rotation
      scene.currentFaceIndex = 0;

      // Ground line
      scene.ground = scene.add.rectangle(
        MILITSA_GAME_CONFIG.width / 2,
        MILITSA_GAME_CONFIG.height - 10,
        MILITSA_GAME_CONFIG.width,
        MILITSA_GAME_CONFIG.groundHeight,
        MILITSA_GAME_CONFIG.groundColor
      );
      scene.physics.add.existing(scene.ground, true);

      // Click ball to boost it up and add random horizontal velocity
      scene.ball.on('pointerdown', () => {
        if (!scene.gameOver) {
          scene.ball.body.setVelocityY(MILITSA_GAME_CONFIG.ballBoostVelocity);
          scene.ball.body.setVelocityX(
            Phaser.Math.Between(
              MILITSA_GAME_CONFIG.horizontalVelocityRange.min,
              MILITSA_GAME_CONFIG.horizontalVelocityRange.max
            )
          );

          // Rotate to next face
          scene.currentFaceIndex = (scene.currentFaceIndex + 1) % MILITSA_GAME_CONFIG.ballFaces.length;
          scene.ball.setTexture(MILITSA_GAME_CONFIG.ballFaces[scene.currentFaceIndex].key);

          scene.score += 1;
          scene.scoreText.setText('Score: ' + scene.score);
        }
      });

      // Check collision with ground
      scene.physics.add.overlap(scene.ball, scene.ground, () => {
        if (!scene.gameOver) {
          scene.gameOver = true;

          // Stop ball physics
          scene.ball.body.setVelocity(0, 0);
          scene.physics.pause();

          // Call the onGameOver callback with score, firstName, and lastName
          if (onGameOver) {
            onGameOver(scene.score, firstName, lastName);
          }

          // Game over text
          scene.add.text(
            MILITSA_GAME_CONFIG.width / 2,
            250,
            'Game Over!',
            MILITSA_TEXT_STYLES.gameOver
          ).setOrigin(0.5);

          scene.add.text(
            MILITSA_GAME_CONFIG.width / 2,
            310,
            'Score: ' + scene.score,
            MILITSA_TEXT_STYLES.finalScore
          ).setOrigin(0.5);

          scene.add.text(
            MILITSA_GAME_CONFIG.width / 2,
            360,
            'Click to restart',
            MILITSA_TEXT_STYLES.restart
          ).setOrigin(0.5);

          // Restart on click
          scene.input.once('pointerdown', () => {
            scene.scene.restart();
          });
        }
      });
    }
  };
}
