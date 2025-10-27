import React, { lazy, Suspense } from 'react';
import { useSelector } from 'react-redux';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter';
import { useGetScoreboardQuery, useSubmitScoreMutation } from '../../services/daphne';
import { useGetUserQuery } from '../../services/gizmo';
import '../../App.css';

// Lazy load game components to keep them out of main bundle
const PrithamPhaserGame = lazy(() => import('../../components/games/PrithamPhaserGame'));
const GameScoreboard = lazy(() => import('../../components/GameScoreboard'));

export function Pritham() {
    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState);

    // Fetch user data to get first and last name
    const { data: userData } = useGetUserQuery({ 'X-First-Last': loginHeaderState }, {
        skip: !loginHeaderState,
    });

    // Fetch scoreboard data from API for pritham game
    const { data: scoreboardData, isLoading: isLoadingScoreboard } = useGetScoreboardQuery('pritham');
    const [submitScore] = useSubmitScoreMutation();

    const firstName = userData?.user?.first || '';
    const lastName = userData?.user?.last || '';
    const currentHighScore = userData?.user?.high_score_pritham || 0;

    const pageMainColor = "cyan";
    const pageSecondaryColor = "terracotta";
    const pageTertiaryColor = "plum";
    const pageSection = "info";

    const handleGameOver = async (score, first, last) => {
        console.log(`Game Over! User: ${first} ${last}, Score: ${score}, Current High Score: ${currentHighScore}`);
        console.log('Submitting with data:', { score, first, last, loginHeaderState });

        // Only submit score to API if it's a new high score
        if (score > currentHighScore) {
            console.log('New high score! Submitting to API...');
            try {
                const result = await submitScore({
                    headers: { 'X-First-Last': loginHeaderState },
                    scoreData: { score, first, last, game: 'pritham' }
                }).unwrap();

                console.log('Score submitted successfully:', result);

                // Only refetch scoreboard if submission was successful and it was a high score
                if (result.isHighScore) {
                    console.log('Refreshing scoreboard...');
                    // The RTK Query cache invalidation will automatically refetch
                }
            } catch (error) {
                console.error('Failed to submit score:', error);
            }
        } else {
            console.log(`Score ${score} is not higher than current high score ${currentHighScore}. Not submitting.`);
        }
    };

    if (!loginHeaderState) {
        return (
            <CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                <h1>Please log in first!</h1>
                <p>Enter your name on the home page to access the game.</p>
            </CardStackPage>
        );
    }

    return (
        <>
            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor}>
                <a href="/" className="btn-23"><marquee>Home</marquee></a>
            </CardStackFooter>
            <CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection} customClass="game-card">
                <div style={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    padding: '15px 20px 150px 40px',
                    overflow: 'hidden'
                }}>
                    <h1 style={{ marginBottom: '15px', marginTop: '5px', fontSize: '28px' }}>Stop Pritham</h1>
                    <Suspense fallback={<div style={{color: '#ffffff', textAlign: 'center', padding: '40px'}}>Loading game...</div>}>
                        <div style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '15px',
                            justifyContent: 'flex-start',
                            alignItems: 'center',
                            width: '100%',
                            maxWidth: '350px'
                        }}>
                            <PrithamPhaserGame
                                onGameOver={handleGameOver}
                                firstName={firstName}
                                lastName={lastName}
                            />
                            {!isLoadingScoreboard && scoreboardData && (
                                <GameScoreboard topScores={scoreboardData} />
                            )}
                        </div>
                    </Suspense>
                </div>
            </CardStackPage>
        </>
    );
}
