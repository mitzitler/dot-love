import Phaser from 'phaser';
import { GAME_CONFIG, TEXT_STYLES } from './gameConfig';

export function createGameScene(onGameOver, firstName, lastName) {
  return {
    preload: function() {
      // TODO: To load assets from CDN, add them here in preload()
      // Example: Load a ball sprite from the CDN instead of using a circle
      // 1. Upload ball.png to the game assets S3 bucket (after deploying CDK stack)
      // 2. Uncomment the line below to load it:
      // this.load.image('ball', 'https://cdn.mitzimatthew.love/game/ball.png');
      //
      // Other examples:
      // this.load.audio('bounce', 'https://cdn.mitzimatthew.love/game/bounce.mp3');
      // this.load.image('background', 'https://cdn.mitzimatthew.love/game/bg.jpg');
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

      // Create ball (currently using procedural circle)
      // TODO: To use a sprite instead, replace this with:
      // scene.ball = scene.add.sprite(GAME_CONFIG.width / 2, 200, 'ball');
      // scene.ball.setDisplaySize(GAME_CONFIG.ballRadius * 2, GAME_CONFIG.ballRadius * 2);
      scene.ball = scene.add.circle(
        GAME_CONFIG.width / 2,
        200,
        GAME_CONFIG.ballRadius,
        GAME_CONFIG.ballColor
      );
      scene.physics.add.existing(scene.ball);
      scene.ball.body.setBounce(0.3);
      scene.ball.body.setCollideWorldBounds(true);
      scene.ball.setInteractive();

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
