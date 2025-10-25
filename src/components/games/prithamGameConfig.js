export const PRITHAM_GAME_CONFIG = {
  width: 800,
  height: 600,
  backgroundColor: '#87CEEB', // Sky blue
  backgroundImage: {
    key: 'pritham-background',
    url: 'https://cdn.mitzimatthew.love/game/pritham_background.jpg'
  },
  gravity: 200, // Low gravity for helicopter

  // Helicopter settings
  helicopterX: 150, // Fixed X position on left side
  helicopterStartY: 300,
  helicopterBoostVelocity: -300, // Upward boost on click
  helicopterAsset: {
    key: 'helicopter',
    url: 'https://cdn.mitzimatthew.love/game/pritham-helicopter.png'
  },
  helicopterSize: { width: 80, height: 60 },

  // Bullet settings
  bulletSpeed: 500,
  bulletCooldown: 200, // ms between shots
  bulletAsset: {
    key: 'bullet',
    url: 'https://cdn.mitzimatthew.love/game/pritham-bullet.png'
  },
  bulletSize: { width: 20, height: 10 },

  // Monster settings
  monsterSpeed: 100,
  monsterSpawnInterval: 3000, // ms
  monsterAsset: {
    key: 'monster',
    url: 'https://cdn.mitzimatthew.love/game/pritham-monster.png'
  },
  monsterSize: { width: 60, height: 60 },

  // Game settings
  pointsPerKill: 10
};

export const PRITHAM_TEXT_STYLES = {
  score: {
    fontSize: '28px',
    color: '#000000'
  },
  instructions: {
    fontSize: '16px',
    color: '#333333'
  },
  gameOver: {
    fontSize: '42px',
    color: '#ff0000'
  },
  finalScore: {
    fontSize: '28px',
    color: '#000000'
  },
  restart: {
    fontSize: '20px',
    color: '#666666'
  }
};
