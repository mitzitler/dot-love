import Phaser from 'phaser';
import { GAME_CONFIG, TEXT_STYLES } from './gameConfig';

export function createGameScene(onGameOver, firstName, lastName) {
  return {
    preload: function() {
      // Load all 3 face images from CDN
      GAME_CONFIG.ballFaces.forEach(face => {
        this.load.image(face.key, face.url);
      });
    },

    create: function() {
      const scene = this;
      scene.score = 0;
      scene.gameOver = false;

      // Score text
      scene.scoreText = scene.add.text(
        GAME_CONFIG.width / 2,
        30,
        'Score: 0',
        TEXT_STYLES.score
      ).setOrigin(0.5);

      // Instructions
      scene.instructionText = scene.add.text(
        GAME_CONFIG.width / 2,
        65,
        'Click to keep it up!',
        TEXT_STYLES.instructions
      ).setOrigin(0.5);

      // Create ball sprite with first face
      scene.ball = scene.add.sprite(
        GAME_CONFIG.width / 2,
        200,
        GAME_CONFIG.ballFaces[0].key
      );
      scene.ball.setDisplaySize(GAME_CONFIG.ballDisplaySize, GAME_CONFIG.ballDisplaySize);
      scene.physics.add.existing(scene.ball);
      scene.ball.body.setBounce(0.3);
      scene.ball.body.setCollideWorldBounds(true);
      scene.ball.setInteractive();

      // Track current face index for rotation
      scene.currentFaceIndex = 0;

      // Ground line
      scene.ground = scene.add.rectangle(
        GAME_CONFIG.width / 2,
        GAME_CONFIG.height - 10,
        GAME_CONFIG.width,
        GAME_CONFIG.groundHeight,
        GAME_CONFIG.groundColor
      );
      scene.physics.add.existing(scene.ground, true);

      // Click ball to boost it up and add random horizontal velocity
      scene.ball.on('pointerdown', () => {
        if (!scene.gameOver) {
          scene.ball.body.setVelocityY(GAME_CONFIG.ballBoostVelocity);
          scene.ball.body.setVelocityX(
            Phaser.Math.Between(
              GAME_CONFIG.horizontalVelocityRange.min,
              GAME_CONFIG.horizontalVelocityRange.max
            )
          );

          // Rotate to next face
          scene.currentFaceIndex = (scene.currentFaceIndex + 1) % GAME_CONFIG.ballFaces.length;
          scene.ball.setTexture(GAME_CONFIG.ballFaces[scene.currentFaceIndex].key);

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
            GAME_CONFIG.width / 2,
            250,
            'Game Over!',
            TEXT_STYLES.gameOver
          ).setOrigin(0.5);

          scene.add.text(
            GAME_CONFIG.width / 2,
            310,
            'Score: ' + scene.score,
            TEXT_STYLES.finalScore
          ).setOrigin(0.5);

          scene.add.text(
            GAME_CONFIG.width / 2,
            360,
            'Click to restart',
            TEXT_STYLES.restart
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
