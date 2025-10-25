import { useEffect, useRef } from 'react';
import Phaser from 'phaser';
import { MILITSA_GAME_CONFIG } from './militsaGameConfig';
import { createMilitsaGameScene } from './militsaGameScene';

function MilitsaPhaserGame({ onGameOver, firstName, lastName }) {
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
      width: MILITSA_GAME_CONFIG.width,
      height: MILITSA_GAME_CONFIG.height,
      parent: gameRef.current,
      backgroundColor: MILITSA_GAME_CONFIG.backgroundColor,
      scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
        parent: gameRef.current,
        width: MILITSA_GAME_CONFIG.width,
        height: MILITSA_GAME_CONFIG.height
      },
      physics: {
        default: 'arcade',
        arcade: {
          gravity: { y: MILITSA_GAME_CONFIG.gravity },
          debug: false
        }
      },
      scene: createMilitsaGameScene(stableOnGameOver, firstNameRef.current, lastNameRef.current)
    };

    phaserGameRef.current = new Phaser.Game(config);

    return () => {
      phaserGameRef.current?.destroy(true);
      phaserGameRef.current = null;
    };
  }, []); // Empty dependency array - only create once

  return <div ref={gameRef} style={{ maxWidth: '100%', width: '320px' }} />;
}

export default MilitsaPhaserGame;
