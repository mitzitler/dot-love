import Phaser from 'phaser';
import { PRITHAM_GAME_CONFIG, PRITHAM_TEXT_STYLES } from './prithamGameConfig';

function loadAssets(scene) {
  scene.load.image(PRITHAM_GAME_CONFIG.backgroundImage.key, PRITHAM_GAME_CONFIG.backgroundImage.url);
  scene.load.image(PRITHAM_GAME_CONFIG.helicopterAsset.key, PRITHAM_GAME_CONFIG.helicopterAsset.url);
  scene.load.image(PRITHAM_GAME_CONFIG.bulletAsset.key, PRITHAM_GAME_CONFIG.bulletAsset.url);
  scene.load.image(PRITHAM_GAME_CONFIG.monsterAsset.key, PRITHAM_GAME_CONFIG.monsterAsset.url);
}

function setupBackground(scene) {
  scene.add.image(
    PRITHAM_GAME_CONFIG.width / 2,
    PRITHAM_GAME_CONFIG.height / 2,
    PRITHAM_GAME_CONFIG.backgroundImage.key
  ).setDisplaySize(PRITHAM_GAME_CONFIG.width, PRITHAM_GAME_CONFIG.height);
}

function setupUI(scene) {
  scene.scoreText = scene.add.text(
    PRITHAM_GAME_CONFIG.width / 2,
    30,
    'Score: 0',
    PRITHAM_TEXT_STYLES.score
  ).setOrigin(0.5);

  scene.instructionText = scene.add.text(
    PRITHAM_GAME_CONFIG.width / 2,
    65,
    'Left side: Boost helicopter | Right side: Shoot',
    PRITHAM_TEXT_STYLES.instructions
  ).setOrigin(0.5);
}

function createHelicopter(scene) {
  const helicopter = scene.physics.add.sprite(
    PRITHAM_GAME_CONFIG.helicopterX,
    PRITHAM_GAME_CONFIG.helicopterStartY,
    PRITHAM_GAME_CONFIG.helicopterAsset.key
  );

  helicopter.setDisplaySize(
    PRITHAM_GAME_CONFIG.helicopterSize.width,
    PRITHAM_GAME_CONFIG.helicopterSize.height
  );
  helicopter.setCollideWorldBounds(true);

  return helicopter;
}

function initializeGroups(scene) {
  scene.bullets = scene.physics.add.group();
  scene.lastBulletTime = 0;
  scene.monsters = scene.physics.add.group();
}

function createShootBulletFunction(scene) {
  return function() {
    const now = scene.time.now;

    if (now - scene.lastBulletTime < PRITHAM_GAME_CONFIG.bulletCooldown) {
      return;
    }

    const bullet = scene.bullets.create(
      scene.helicopter.x + 40,
      scene.helicopter.y,
      PRITHAM_GAME_CONFIG.bulletAsset.key
    );

    bullet.setDisplaySize(
      PRITHAM_GAME_CONFIG.bulletSize.width,
      PRITHAM_GAME_CONFIG.bulletSize.height
    );
    bullet.setVelocityX(PRITHAM_GAME_CONFIG.bulletSpeed);

    scene.lastBulletTime = now;
  };
}

function createSpawnMonsterFunction(scene) {
  return function() {
    if (scene.gameOver) return;

    const randomY = Phaser.Math.Between(50, PRITHAM_GAME_CONFIG.height - 50);

    const monster = scene.monsters.create(
      PRITHAM_GAME_CONFIG.width + 50,
      randomY,
      PRITHAM_GAME_CONFIG.monsterAsset.key
    );

    monster.setDisplaySize(
      PRITHAM_GAME_CONFIG.monsterSize.width,
      PRITHAM_GAME_CONFIG.monsterSize.height
    );
    monster.setVelocityX(-PRITHAM_GAME_CONFIG.monsterSpeed);
  };
}

function createEndGameFunction(scene, onGameOver, firstName, lastName) {
  return function() {
    if (scene.gameOver) return;

    scene.gameOver = true;
    scene.physics.pause();

    if (onGameOver) {
      onGameOver(scene.score, firstName, lastName);
    }

    scene.add.text(
      PRITHAM_GAME_CONFIG.width / 2,
      250,
      'Game Over!',
      PRITHAM_TEXT_STYLES.gameOver
    ).setOrigin(0.5);

    scene.add.text(
      PRITHAM_GAME_CONFIG.width / 2,
      310,
      'Score: ' + scene.score,
      PRITHAM_TEXT_STYLES.finalScore
    ).setOrigin(0.5);

    scene.add.text(
      PRITHAM_GAME_CONFIG.width / 2,
      360,
      'Click to restart',
      PRITHAM_TEXT_STYLES.restart
    ).setOrigin(0.5);

    scene.input.once('pointerdown', () => {
      scene.scene.restart();
    });
  };
}

function setupControls(scene) {
  const leftZone = scene.add.zone(
    0,
    0,
    PRITHAM_GAME_CONFIG.width / 2,
    PRITHAM_GAME_CONFIG.height
  ).setOrigin(0, 0).setInteractive();

  const rightZone = scene.add.zone(
    PRITHAM_GAME_CONFIG.width / 2,
    0,
    PRITHAM_GAME_CONFIG.width / 2,
    PRITHAM_GAME_CONFIG.height
  ).setOrigin(0, 0).setInteractive();

  leftZone.on('pointerdown', () => {
    if (!scene.gameOver) {
      scene.helicopter.body.setVelocityY(PRITHAM_GAME_CONFIG.helicopterBoostVelocity);
    }
  });

  rightZone.on('pointerdown', () => {
    if (!scene.gameOver) {
      scene.shootBullet();
    }
  });
}

function setupCollisions(scene) {
  scene.physics.add.overlap(scene.bullets, scene.monsters, (bullet, monster) => {
    bullet.destroy();
    monster.destroy();
    scene.score += PRITHAM_GAME_CONFIG.pointsPerKill;
    scene.scoreText.setText('Score: ' + scene.score);
  });

  scene.physics.add.overlap(scene.helicopter, scene.monsters, () => {
    if (!scene.gameOver) {
      scene.endGame();
    }
  });
}

function setupMonsterSpawning(scene) {
  scene.time.addEvent({
    delay: PRITHAM_GAME_CONFIG.monsterSpawnInterval,
    callback: scene.spawnMonster,
    callbackScope: scene,
    loop: true
  });

  scene.time.delayedCall(1000, scene.spawnMonster, [], scene);
}

function cleanupBullets(scene) {
  scene.bullets.children.entries.forEach(bullet => {
    if (bullet.x > PRITHAM_GAME_CONFIG.width) {
      bullet.destroy();
    }
  });
}

function checkMonsterEdge(scene) {
  scene.monsters.children.entries.forEach(monster => {
    if (monster.x < -50) {
      scene.endGame();
    }
  });
}

export function createPrithamGameScene(onGameOver, firstName, lastName) {
  return {
    preload: function() {
      loadAssets(this);
    },

    create: function() {
      const scene = this;
      scene.score = 0;
      scene.gameOver = false;

      setupBackground(scene);
      scene.physics.world.gravity.y = PRITHAM_GAME_CONFIG.gravity;
      setupUI(scene);
      scene.helicopter = createHelicopter(scene);
      initializeGroups(scene);

      scene.shootBullet = createShootBulletFunction(scene);
      scene.spawnMonster = createSpawnMonsterFunction(scene);
      scene.endGame = createEndGameFunction(scene, onGameOver, firstName, lastName);

      setupControls(scene);
      setupCollisions(scene);
      setupMonsterSpawning(scene);
    },

    update: function() {
      const scene = this;
      if (scene.gameOver) return;

      cleanupBullets(scene);
      checkMonsterEdge(scene);
    }
  };
}
