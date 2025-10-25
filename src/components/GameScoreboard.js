import React from 'react';

function GameScoreboard({ topScores }) {
  if (!topScores || topScores.length === 0) {
    return (
      <div style={{
        width: '250px',
        padding: '20px',
        backgroundColor: '#1a1a1a',
        borderRadius: '10px'
      }}>
        <h2 style={{
          color: '#ffffff',
          marginTop: 0,
          marginBottom: '20px',
          fontSize: '24px',
          textAlign: 'center'
        }}>
          Top 5
        </h2>
        <p style={{ color: '#aaaaaa', textAlign: 'center' }}>No scores yet!</p>
      </div>
    );
  }

  return (
    <div style={{
      width: '320px',
      maxWidth: '100%',
      padding: '15px',
      backgroundColor: '#1a1a1a',
      borderRadius: '10px',
      position: 'relative',
      zIndex: 10
    }}>
      <h2 style={{
        color: '#ffffff',
        marginTop: 0,
        marginBottom: '20px',
        fontSize: '24px',
        textAlign: 'center'
      }}>
        Top 5
      </h2>
      <ol style={{
        color: '#ffffff',
        padding: '0 0 0 25px',
        margin: 0,
        listStylePosition: 'outside',
        listStyle: 'decimal'
      }}>
        {topScores.map((entry, index) => (
          <li key={index} style={{
            marginBottom: '15px',
            fontSize: '16px',
            paddingLeft: '5px',
            color: '#ffffff',
            display: 'list-item'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: '10px'
            }}>
              <span style={{
                color: '#ffffff',
                flexGrow: 1,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                fontSize: '16px'
              }}>
                {entry.userName}
              </span>
              <span style={{
                color: '#ff6600',
                fontWeight: 'bold',
                flexShrink: 0,
                minWidth: '40px',
                textAlign: 'right',
                fontSize: '16px'
              }}>
                {entry.score}
              </span>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

export default GameScoreboard;
