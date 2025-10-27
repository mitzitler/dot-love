import Phaser from 'phaser';
import { MILITSA_GAME_CONFIG, MILITSA_TEXT_STYLES } from './militsaGameConfig';

function createBall(scene, x, y, faceIndex) {
  const ball = scene.add.sprite(x, y, MILITSA_GAME_CONFIG.ballFaces[0].key);
  ball.setDisplaySize(MILITSA_GAME_CONFIG.ballDisplaySize, MILITSA_GAME_CONFIG.ballDisplaySize);
  scene.physics.add.existing(ball);
  ball.body.setBounce(0.3);
  ball.body.setCollideWorldBounds(true);
  ball.setInteractive();
  ball.body.setGravityY(MILITSA_GAME_CONFIG.gravity);
  ball.faceIndex = faceIndex;
  return ball;
}

function boostBall(ball) {
  // Give it a good kick upward
  ball.body.setVelocityY(MILITSA_GAME_CONFIG.ballBoostVelocity);
  // Toss in some random sideways movement to keep things interesting
  ball.body.setVelocityX(
    Phaser.Math.Between(
      MILITSA_GAME_CONFIG.horizontalVelocityRange.min,
      MILITSA_GAME_CONFIG.horizontalVelocityRange.max
    )
  );
}

function rotateBallFace(ball) {
  // Cycle through the different faces
  ball.faceIndex = (ball.faceIndex + 1) % MILITSA_GAME_CONFIG.ballFaces.length;
  ball.setTexture(MILITSA_GAME_CONFIG.ballFaces[ball.faceIndex].key);
}

function updateGravity(scene, ball) {
  // Between scores 21-39, things get heavier with each tap
  if (scene.score > 20 && scene.score < 40) {
    ball.body.gravity.y += 15;
  }
}

function resetAllGravity(scene) {
  // When ball 3 shows up, reset everything back to normal
  const balls = [scene.balls.ball1, scene.balls.ball2, scene.balls.ball3].filter(b => b);
  balls.forEach(ball => ball.body.setGravityY(MILITSA_GAME_CONFIG.gravity));
}

function handleBallClick(scene, ball) {
  return () => {
    if (!scene.gameOver) {
      boostBall(ball);
      rotateBallFace(ball);
      scene.score += 1;
      scene.scoreText.setText('Score: ' + scene.score);
      updateGravity(scene, ball);
      checkSpawnNewBall(scene);
    }
  };
}

function checkSpawnNewBall(scene) {
  // At 20 points, throw in a second ball to juggle
  if (scene.score === 20 && !scene.balls.ball2) {
    scene.balls.ball2 = createBall(scene, MILITSA_GAME_CONFIG.width / 2, 100, 0);
    scene.balls.ball2.on('pointerdown', handleBallClick(scene, scene.balls.ball2));
    setupGroundCollision(scene, scene.balls.ball2);
  }

  // Hit 40? Time for ball number three, plus we dial the gravity back
  if (scene.score === 40 && !scene.balls.ball3) {
    scene.balls.ball3 = createBall(scene, MILITSA_GAME_CONFIG.width / 2, 50, 0);
    scene.balls.ball3.on('pointerdown', handleBallClick(scene, scene.balls.ball3));
    setupGroundCollision(scene, scene.balls.ball3);
    resetAllGravity(scene);
  }
}

function stopAllBalls(scene) {
  const balls = [scene.balls.ball1, scene.balls.ball2, scene.balls.ball3].filter(b => b);
  balls.forEach(ball => ball.body.setVelocity(0, 0));
}

function showGameOver(scene, onGameOver, firstName, lastName) {
  scene.gameOver = true;
  stopAllBalls(scene);
  scene.physics.pause();

  if (onGameOver) {
    onGameOver(scene.score, firstName, lastName);
  }

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

  scene.input.once('pointerdown', () => {
    scene.scene.restart();
  });
}

function setupGroundCollision(scene, ball) {
  // If the ball hits the floor, game's over
  scene.physics.add.overlap(ball, scene.ground, () => {
    if (!scene.gameOver) {
      showGameOver(scene, scene.onGameOverCallback, scene.firstName, scene.lastName);
    }
  });
}

export function createMilitsaGameScene(onGameOver, firstName, lastName) {
  return {
    preload: function() {
      this.load.image(MILITSA_GAME_CONFIG.backgroundImage.key, MILITSA_GAME_CONFIG.backgroundImage.url);
      MILITSA_GAME_CONFIG.ballFaces.forEach(face => {
        this.load.image(face.key, face.url);
      });
    },

    create: function() {
      const scene = this;
      scene.score = 0;
      scene.gameOver = false;
      scene.balls = {};
      scene.onGameOverCallback = onGameOver;
      scene.firstName = firstName;
      scene.lastName = lastName;

      scene.add.image(
        MILITSA_GAME_CONFIG.width / 2,
        MILITSA_GAME_CONFIG.height / 2,
        MILITSA_GAME_CONFIG.backgroundImage.key
      ).setDisplaySize(MILITSA_GAME_CONFIG.width, MILITSA_GAME_CONFIG.height);

      scene.scoreText = scene.add.text(
        MILITSA_GAME_CONFIG.width / 2,
        30,
        'Score: 0',
        MILITSA_TEXT_STYLES.score
      ).setOrigin(0.5);

      scene.instructionText = scene.add.text(
        MILITSA_GAME_CONFIG.width / 2,
        65,
        'Click to keep it up!',
        MILITSA_TEXT_STYLES.instructions
      ).setOrigin(0.5);

      // Invisible floor for collision detection (no ugly red bar)
      scene.ground = scene.add.rectangle(
        MILITSA_GAME_CONFIG.width / 2,
        MILITSA_GAME_CONFIG.height - 10,
        MILITSA_GAME_CONFIG.width,
        MILITSA_GAME_CONFIG.groundHeight,
        MILITSA_GAME_CONFIG.groundColor
      );
      scene.ground.setVisible(false);
      scene.physics.add.existing(scene.ground, true);

      scene.balls.ball1 = createBall(scene, MILITSA_GAME_CONFIG.width / 2, 200, 0);
      scene.balls.ball1.on('pointerdown', handleBallClick(scene, scene.balls.ball1));
      setupGroundCollision(scene, scene.balls.ball1);
    }
  };
}
