import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { CardStackPage } from '../components/CardStackPage';
import { CardStackFooter } from '../components/CardStackFooter';
import { useSubmitSurveyMutation, useGetSurveyQuery } from '../services/gizmo';
import { toast } from 'react-toastify';
import '../App.css';

export function Survey() {
    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState);
    const [submitSurvey, { isLoading: isSubmitting }] = useSubmitSurveyMutation();
    const { data: existingSurvey, isLoading: isLoadingSurvey } = useGetSurveyQuery(loginHeaderState, {
        skip: !loginHeaderState,
    });

    const [responses, setResponses] = useState({
        attending_events: '',
        dietary_preferences: '',
        song_requests: '',
        accommodation_needed: false,
        transportation_needed: false,
        additional_comments: '',
    });

    const [hasSubmitted, setHasSubmitted] = useState(false);

    useEffect(() => {
        if (existingSurvey && existingSurvey.responses) {
            setResponses(existingSurvey.responses);
            setHasSubmitted(true);
        }
    }, [existingSurvey]);

    const handleInputChange = (field, value) => {
        setResponses({
            ...responses,
            [field]: value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!loginHeaderState) {
            toast.error("Please log in first by entering your name on the home page", {
                theme: "dark",
                position: "top-right",
            });
            return;
        }

        try {
            await submitSurvey({
                headers: loginHeaderState,
                responses,
            }).unwrap();

            toast.success("Survey submitted successfully! Thank you!", {
                theme: "dark",
                position: "top-right",
            });
            setHasSubmitted(true);
        } catch (err) {
            console.error("Survey submission failed:", err);
            toast.error("Failed to submit survey. Please try again.", {
                theme: "dark",
                position: "top-right",
            });
        }
    };

    const pageMainColor = "cyan";
    const pageSecondaryColor = "terracotta";
    const pageTertiaryColor = "plum";
    const pageSection = "info";

    if (!loginHeaderState) {
        return (
            <CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                <h1>Please log in first!</h1>
                <p>Enter your name on the home page to access the survey.</p>
            </CardStackPage>
        );
    }

    if (isLoadingSurvey) {
        return (
            <CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                <p>Loading survey...</p>
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
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                <h1>Wedding Survey</h1>
                {hasSubmitted && (
                    <p style={{color: 'green', marginBottom: '1rem', textAlign: 'center'}}>✓ You've already submitted this survey. You can update your responses below.</p>
                )}
                <form onSubmit={handleSubmit} style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

                    <div style={{width: '100%', maxWidth: '600px'}}>
                        <h2>Which events are you planning to attend?</h2>
                        <textarea
                            id="attending_events"
                            value={responses.attending_events}
                            onChange={(e) => handleInputChange('attending_events', e.target.value)}
                            placeholder="e.g., Ceremony, Reception, After-party..."
                            rows="3"
                            style={{width: '100%', padding: '0.5em', marginBottom: '1.5em', borderRadius: '7px', border: '1px solid #ccc'}}
                        />
                    </div>

                    <div style={{width: '100%', maxWidth: '600px'}}>
                        <h2>Any song requests for the reception?</h2>
                        <textarea
                            id="song_requests"
                            value={responses.song_requests}
                            onChange={(e) => handleInputChange('song_requests', e.target.value)}
                            placeholder="Artist - Song Title"
                            rows="3"
                            style={{width: '100%', padding: '0.5em', marginBottom: '1.5em', borderRadius: '7px', border: '1px solid #ccc'}}
                        />
                    </div>

                    <div style={{width: '100%', maxWidth: '600px', marginBottom: '1.5rem', textAlign: 'left'}}>
                        <label className="checkbox-guest">
                            <input
                                type="checkbox"
                                checked={responses.accommodation_needed}
                                onChange={(e) => handleInputChange('accommodation_needed', e.target.checked)}
                            />
                            <span className="checkmark"></span>
                            I need help finding accommodation
                        </label>
                    </div>

                    <div style={{width: '100%', maxWidth: '600px', marginBottom: '1.5rem', textAlign: 'left'}}>
                        <label className="checkbox-guest">
                            <input
                                type="checkbox"
                                checked={responses.transportation_needed}
                                onChange={(e) => handleInputChange('transportation_needed', e.target.checked)}
                            />
                            <span className="checkmark"></span>
                            I need help with transportation
                        </label>
                    </div>

                    <div style={{width: '100%', maxWidth: '600px'}}>
                        <h2>Any additional comments or questions?</h2>
                        <textarea
                            id="additional_comments"
                            value={responses.additional_comments}
                            onChange={(e) => handleInputChange('additional_comments', e.target.value)}
                            placeholder="Let us know if you have any questions or special needs..."
                            rows="4"
                            style={{width: '100%', padding: '0.5em', marginBottom: '1.5em', borderRadius: '7px', border: '1px solid #ccc'}}
                        />
                    </div>

                    <button type="submit" disabled={isSubmitting} className="btn-generic" style={{marginTop: '1em'}}>
                        {isSubmitting ? 'Submitting...' : hasSubmitted ? 'Update Survey' : 'Submit Survey'}
                    </button>
                </form>
            </CardStackPage>
        </>
    );
}
