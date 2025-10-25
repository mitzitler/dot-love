import { useEffect, useRef } from 'react';
import Phaser from 'phaser';
import { PRITHAM_GAME_CONFIG } from './prithamGameConfig';
import { createPrithamGameScene } from './prithamGameScene';

function PrithamPhaserGame({ onGameOver, firstName, lastName }) {
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
      width: PRITHAM_GAME_CONFIG.width,
      height: PRITHAM_GAME_CONFIG.height,
      parent: gameRef.current,
      backgroundColor: PRITHAM_GAME_CONFIG.backgroundColor,
      physics: {
        default: 'arcade',
        arcade: {
          gravity: { y: PRITHAM_GAME_CONFIG.gravity },
          debug: false
        }
      },
      scene: createPrithamGameScene(stableOnGameOver, firstNameRef.current, lastNameRef.current)
    };

    phaserGameRef.current = new Phaser.Game(config);

    return () => {
      phaserGameRef.current?.destroy(true);
      phaserGameRef.current = null;
    };
  }, []); // Empty dependency array - only create once

  return <div ref={gameRef} />;
}

export default PrithamPhaserGame;
