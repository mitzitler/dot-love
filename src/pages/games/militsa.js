import React, { lazy, Suspense } from 'react';
import { useSelector } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { CardStackPage } from '../../components/CardStackPage';
import { CardStackFooter } from '../../components/CardStackFooter';
import { useSubmitScoreMutation } from '../../services/daphne';
import { useGetUserQuery } from '../../services/gizmo';
import '../../App.css';

// Lazy load game components to keep them out of main bundle
const MilitsaPhaserGame = lazy(() => import('../../components/games/MilitsaPhaserGame'));
const GameScoreboard = lazy(() => import('../../components/GameScoreboard'));

export function Survey() {
    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState);

    // Fetch user data to get first and last name
    const { data: userData } = useGetUserQuery({ 'X-First-Last': loginHeaderState }, {
        skip: !loginHeaderState,
    });

    const [submitScore] = useSubmitScoreMutation();

    const firstName = userData?.user?.first || '';
    const lastName = userData?.user?.last || '';
    const currentHighScore = userData?.user?.high_score_militsa || 0;

    const pageMainColor = "cyan";
    const pageSecondaryColor = "terracotta";
    const pageTertiaryColor = "plum";
    const pageSection = "info";

    const handleGameOver = async (score, first, last) => {
        // Submit ALL scores (backend will handle high score logic and scoreboard updates)
        try {
            await submitScore({
                headers: { 'X-First-Last': loginHeaderState },
                scoreData: { score, first, last, game: 'militsa' }
            }).unwrap();
        } catch (error) {
            console.error('Failed to submit score:', error);
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
                <NavLink to="/" className="btn-23"><marquee>INFO → </marquee></NavLink>
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
                    <img
                        src="https://cdn.mitzimatthew.love/game/ddm_title.png"
                        alt="Don't Drop Militsa"
                        style={{ marginBottom: '0px', marginTop: '5px', width: '80%', maxWidth: '250px', height: 'auto' }}
                    />
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
                            <MilitsaPhaserGame
                                onGameOver={handleGameOver}
                                firstName={firstName}
                                lastName={lastName}
                            />
                            <GameScoreboard game="militsa" />
                        </div>
                    </Suspense>
                </div>
            </CardStackPage>
        </>
    );
}
