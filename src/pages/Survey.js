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
    const pageSection = "survey";

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
            <CardStackPage pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                <div className="survey-container">
                    <h1>Wedding Survey</h1>
                    {hasSubmitted && (
                        <p className="text-green-600 mb-4">✓ You've already submitted this survey. You can update your responses below.</p>
                    )}
                    <form onSubmit={handleSubmit} className="survey-form">

                        <div className="form-group">
                            <label htmlFor="attending_events">
                                Which events are you planning to attend?
                            </label>
                            <textarea
                                id="attending_events"
                                value={responses.attending_events}
                                onChange={(e) => handleInputChange('attending_events', e.target.value)}
                                placeholder="e.g., Ceremony, Reception, After-party..."
                                rows="3"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="song_requests">
                                Any song requests for the reception?
                            </label>
                            <textarea
                                id="song_requests"
                                value={responses.song_requests}
                                onChange={(e) => handleInputChange('song_requests', e.target.value)}
                                placeholder="Artist - Song Title"
                                rows="3"
                            />
                        </div>

                        <div className="form-group">
                            <label>
                                <input
                                    type="checkbox"
                                    checked={responses.accommodation_needed}
                                    onChange={(e) => handleInputChange('accommodation_needed', e.target.checked)}
                                />
                                I need help finding accommodation
                            </label>
                        </div>

                        <div className="form-group">
                            <label>
                                <input
                                    type="checkbox"
                                    checked={responses.transportation_needed}
                                    onChange={(e) => handleInputChange('transportation_needed', e.target.checked)}
                                />
                                I need help with transportation
                            </label>
                        </div>

                        <div className="form-group">
                            <label htmlFor="additional_comments">
                                Any additional comments or questions?
                            </label>
                            <textarea
                                id="additional_comments"
                                value={responses.additional_comments}
                                onChange={(e) => handleInputChange('additional_comments', e.target.value)}
                                placeholder="Let us know if you have any questions or special needs..."
                                rows="4"
                            />
                        </div>

                        <button type="submit" disabled={isSubmitting} className="submit-button">
                            {isSubmitting ? 'Submitting...' : hasSubmitted ? 'Update Survey' : 'Submit Survey'}
                        </button>
                    </form>
                </div>
            </CardStackPage>

            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor}>
                <a href="/" className="btn-23"><marquee>Home</marquee></a>
            </CardStackFooter>
        </>
    );
}
