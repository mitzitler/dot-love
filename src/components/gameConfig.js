export const GAME_CONFIG = {
  width: 400,
  height: 600,
  backgroundColor: '#2d2d2d',
  gravity: 400,
  ballRadius: 50,
  ballColor: 0xff6600,
  ballFaces: [
    { key: 'militsa-face-1', url: 'https://cdn.mitzimatthew.love/game/militsa_1.jpg' },
    { key: 'militsa-face-2', url: 'https://cdn.mitzimatthew.love/game/militsa_2.jpg' },
    { key: 'militsa-face-3', url: 'https://cdn.mitzimatthew.love/game/militsa_3.jpg' }
  ],
  ballDisplaySize: 100,
  groundColor: 0xff0000,
  groundHeight: 20,
  ballBoostVelocity: -350,
  horizontalVelocityRange: { min: -200, max: 200 }
};

export const TEXT_STYLES = {
  score: {
    fontSize: '28px',
    color: '#ffffff'
  },
  instructions: {
    fontSize: '16px',
    color: '#aaaaaa'
  },
  gameOver: {
    fontSize: '42px',
    color: '#ff0000'
  },
  finalScore: {
    fontSize: '28px',
    color: '#ffffff'
  },
  restart: {
    fontSize: '20px',
    color: '#aaaaaa'
  }
};
