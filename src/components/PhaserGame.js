import { useEffect, useRef } from 'react';
import Phaser from 'phaser';
import { GAME_CONFIG } from './gameConfig';
import { createGameScene } from './gameScene';

function PhaserGame({ onGameOver, firstName, lastName }) {
  const gameRef = useRef(null);
  const phaserGameRef = useRef(null);
  const onGameOverRef = useRef(onGameOver);
  const firstNameRef = useRef(firstName);
  const lastNameRef = useRef(lastName);

  // Update refs when props change without recreating the game
  useEffect(() => {
    onGameOverRef.current = onGameOver;
    firstNameRef.current = firstName;
    lastNameRef.current = lastName;
  }, [onGameOver, firstName, lastName]);

  useEffect(() => {
    if (phaserGameRef.current) return;

    // Stable callback that uses refs
    const stableOnGameOver = (score, first, last) => {
      if (onGameOverRef.current) {
        onGameOverRef.current(score, first, last);
      }
    };

    const config = {
      type: Phaser.AUTO,
      width: GAME_CONFIG.width,
      height: GAME_CONFIG.height,
      parent: gameRef.current,
      backgroundColor: GAME_CONFIG.backgroundColor,
      physics: {
        default: 'arcade',
        arcade: {
          gravity: { y: GAME_CONFIG.gravity },
          debug: false
        }
      },
      scene: createGameScene(stableOnGameOver, firstNameRef.current, lastNameRef.current)
    };

    phaserGameRef.current = new Phaser.Game(config);

    return () => {
      phaserGameRef.current?.destroy(true);
      phaserGameRef.current = null;
    };
  }, []); // Empty dependency array - only create once

  return <div ref={gameRef} />;
}

export default PhaserGame;
