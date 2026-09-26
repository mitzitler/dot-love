import React, { useCallback, useEffect, useState } from "react";
import {
    Button,
    Chip,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    IconButton,
    MenuItem,
    Select,
    TextField,
} from "@mui/material";
import ArrowBackIosNewIcon from "@mui/icons-material/ArrowBackIosNew";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import CallSplitIcon from "@mui/icons-material/CallSplit";
import CardGiftcardIcon from "@mui/icons-material/CardGiftcard";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import LocalShippingIcon from "@mui/icons-material/LocalShipping";
import PhoneIcon from "@mui/icons-material/Phone";
import RefreshIcon from "@mui/icons-material/Refresh";
import { toast } from "react-toastify";
import SortTableLetters from "./SortTableLetters";
import {
    useSyncLettersMutation,
    useCreateLetterMutation,
    useUpdateLetterMutation,
    useDeleteLetterMutation,
    useDisjoinLetterPairMutation,
} from "../../services/letters";

const STATUS_OPTIONS = ["DRAFT", "WRITTEN", "READY_TO_SEND", "SENT"];

const STATUS_CHIP_COLOR = {
    DRAFT: "info",
    WRITTEN: "warning",
    READY_TO_SEND: "success",
    SENT: "secondary",
};

// Max handwritten message length (greeting + body) Handwrytten fits on a
// card; the envelope address and sign-off are separate. Mirrors
// LETTER_BODY_MAX_CHARS in the miatun lambda.
export const LETTER_BODY_MAX_CHARS = 500;

const EMPTY_NEW_LETTER = {
    guest: "",
    partner: "",
    gift: "",
    brand: "",
    price_dollars: "",
    phone: "",
    street: "",
    second_line: "",
    city: "",
    state_loc: "",
    zipcode: "",
    country: "",
};

function formatPriceCents(priceCents) {
    if (priceCents === null || priceCents === undefined) return "";
    return "$" + (priceCents / 100).toFixed(2);
}

const toastOptions = { theme: "dark", position: "top-right", autoClose: 3000 };

export function LettersAdmin({ letters, setLetters, apiKey, triggerGetAllLetters }) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [bodyDraft, setBodyDraft] = useState("");
    const [statusDraft, setStatusDraft] = useState("DRAFT");
    const [showNewLetterForm, setShowNewLetterForm] = useState(false);
    const [newLetterForm, setNewLetterForm] = useState(EMPTY_NEW_LETTER);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [disjoinDialogOpen, setDisjoinDialogOpen] = useState(false);

    const [syncLetters, { isLoading: isSyncing }] = useSyncLettersMutation();
    const [createLetter, { isLoading: isCreating }] = useCreateLetterMutation();
    const [updateLetter, { isLoading: isSaving }] = useUpdateLetterMutation();
    const [deleteLetter, { isLoading: isDeleting }] = useDeleteLetterMutation();
    const [disjoinLetterPair, { isLoading: isDisjoining }] = useDisjoinLetterPairMutation();

    const currentLetter = letters && letters.length > 0 ? letters[currentIndex] : null;

    useEffect(() => {
        if (currentLetter) {
            setBodyDraft(currentLetter.letter_body || "");
            setStatusDraft(currentLetter.status || "DRAFT");
        } else {
            setBodyDraft("");
            setStatusDraft("DRAFT");
        }
    }, [currentLetter]);

    useEffect(() => {
        if (letters && currentIndex >= letters.length) {
            setCurrentIndex(Math.max(0, letters.length - 1));
        }
    }, [letters, currentIndex]);

    const handleSync = async () => {
        try {
            await syncLetters(apiKey).unwrap();
            const refreshed = await triggerGetAllLetters(apiKey).unwrap();
            setLetters(refreshed.letters);
            toast.success("Synced letters from claims.", toastOptions);
        } catch (err) {
            console.error("Failed to sync letters:", err);
            toast.error("Failed to sync letters from claims.", toastOptions);
        }
    };

    const handleNewLetterFieldChange = (field) => (e) => {
        setNewLetterForm((prev) => ({ ...prev, [field]: e.target.value }));
    };

    const handleCreateLetter = async (e) => {
        e.preventDefault();
        const priceDollars = parseFloat(newLetterForm.price_dollars);
        const { gift, brand, price_dollars, ...contactFields } = newLetterForm;
        const letterData = {
            ...contactFields,
            gifts: [
                {
                    gift,
                    brand,
                    price_cents: isNaN(priceDollars) ? null : Math.round(priceDollars * 100),
                },
            ],
        };

        try {
            const result = await createLetter({ apiKey, letterData }).unwrap();
            const updatedLetters = [...(letters || []), result.letter];
            setLetters(updatedLetters);
            setCurrentIndex(updatedLetters.length - 1);
            setNewLetterForm(EMPTY_NEW_LETTER);
            setShowNewLetterForm(false);
            toast.success("Letter created.", toastOptions);
        } catch (err) {
            console.error("Failed to create letter:", err);
            toast.error("Failed to create letter.", toastOptions);
        }
    };

    const handleSave = async () => {
        if (!currentLetter) return;
        try {
            const result = await updateLetter({
                apiKey,
                letterId: currentLetter.id,
                updates: { letter_body: bodyDraft, status: statusDraft },
            }).unwrap();
            setLetters(
                letters.map((letter) =>
                    letter.id === result.letter.id ? result.letter : letter
                )
            );
            toast.success("Letter saved.", toastOptions);
        } catch (err) {
            console.error("Failed to save letter:", err);
            toast.error("Failed to save letter.", toastOptions);
        }
    };

    const handleDeleteConfirmed = async () => {
        if (!currentLetter) return;
        const letterId = currentLetter.id;
        try {
            await deleteLetter({ apiKey, letterId }).unwrap();
            const updatedLetters = letters.filter((letter) => letter.id !== letterId);
            setLetters(updatedLetters);
            setCurrentIndex((index) => Math.max(0, Math.min(index, updatedLetters.length - 1)));
            toast.success("Letter deleted.", toastOptions);
        } catch (err) {
            console.error("Failed to delete letter:", err);
            toast.error("Failed to delete letter.", toastOptions);
        } finally {
            setDeleteDialogOpen(false);
        }
    };

    const handleDisjoinConfirmed = async () => {
        if (!currentLetter) return;
        const originalClaimantId = currentLetter.claimant_id;
        try {
            await disjoinLetterPair({ apiKey, letterId: currentLetter.id }).unwrap();
            const refreshed = await triggerGetAllLetters(apiKey).unwrap();
            setLetters(refreshed.letters);
            const newIndex = refreshed.letters.findIndex(
                (letter) => letter.claimant_id === originalClaimantId
            );
            if (newIndex !== -1) setCurrentIndex(newIndex);
            toast.success("Split into separate letters.", toastOptions);
        } catch (err) {
            console.error("Failed to disjoin letter pair:", err);
            toast.error("Failed to split the letter pair.", toastOptions);
        } finally {
            setDisjoinDialogOpen(false);
        }
    };

    const handleSelectLetter = useCallback((row) => {
        setCurrentIndex((index) => {
            const found = letters.findIndex((letter) => letter.id === row.id);
            return found !== -1 ? found : index;
        });
    }, [letters]);

    const handlePrev = () => setCurrentIndex((index) => Math.max(0, index - 1));
    const handleNext = () =>
        setCurrentIndex((index) => Math.min((letters?.length || 1) - 1, index + 1));

    return (
        <div className="font-suse">
            <div className="my-4 flex gap-3">
                <button
                    type="button"
                    onClick={handleSync}
                    disabled={isSyncing}
                    className="flex items-center gap-2 rounded-full bg-plum-500 px-4 py-2 text-sm font-semibold text-cream-400 shadow-sm transition hover:bg-plum-500/80 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    <RefreshIcon fontSize="small" className={isSyncing ? "animate-spin" : ""} />
                    {isSyncing ? "Syncing..." : "Sync from Claims"}
                </button>
                <button
                    type="button"
                    onClick={() => setShowNewLetterForm((show) => !show)}
                    className="rounded-full border border-terracotta-500 px-4 py-2 text-sm font-semibold text-terracotta-500 transition hover:bg-terracotta-500/10"
                >
                    {showNewLetterForm ? "Cancel" : "+ New Letter"}
                </button>
            </div>

            {showNewLetterForm && (
                <form onSubmit={handleCreateLetter} className="my-4 max-w-[750px] rounded-2xl bg-white/60 p-5 shadow-sm">
                    <p className="mb-2 text-xs font-bold uppercase tracking-wide text-plum-500">Recipient</p>
                    <div className="mb-4 flex flex-wrap gap-2">
                        <TextField label="Guest" size="small" value={newLetterForm.guest} onChange={handleNewLetterFieldChange("guest")} />
                        <TextField label="Partner" size="small" value={newLetterForm.partner} onChange={handleNewLetterFieldChange("partner")} />
                        <TextField label="Phone" size="small" value={newLetterForm.phone} onChange={handleNewLetterFieldChange("phone")} />
                    </div>

                    <p className="mb-2 text-xs font-bold uppercase tracking-wide text-plum-500">Gift</p>
                    <div className="mb-4 flex flex-wrap gap-2">
                        <TextField label="Gift" size="small" value={newLetterForm.gift} onChange={handleNewLetterFieldChange("gift")} />
                        <TextField label="Brand" size="small" value={newLetterForm.brand} onChange={handleNewLetterFieldChange("brand")} />
                        <TextField label="Price ($)" size="small" value={newLetterForm.price_dollars} onChange={handleNewLetterFieldChange("price_dollars")} />
                    </div>

                    <p className="mb-2 text-xs font-bold uppercase tracking-wide text-plum-500">Shipping Address</p>
                    <div className="mb-4 flex flex-wrap gap-2">
                        <TextField label="Street" size="small" value={newLetterForm.street} onChange={handleNewLetterFieldChange("street")} />
                        <TextField label="Line 2" size="small" value={newLetterForm.second_line} onChange={handleNewLetterFieldChange("second_line")} />
                        <TextField label="City" size="small" value={newLetterForm.city} onChange={handleNewLetterFieldChange("city")} />
                        <TextField label="State" size="small" value={newLetterForm.state_loc} onChange={handleNewLetterFieldChange("state_loc")} />
                        <TextField label="Zip" size="small" value={newLetterForm.zipcode} onChange={handleNewLetterFieldChange("zipcode")} />
                        <TextField label="Country" size="small" value={newLetterForm.country} onChange={handleNewLetterFieldChange("country")} />
                    </div>

                    <button
                        type="submit"
                        disabled={isCreating}
                        className="rounded-full bg-terracotta-500 px-5 py-2 text-sm font-semibold text-cream-400 shadow-sm transition hover:bg-terracotta-500/80 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        {isCreating ? "Creating..." : "Create Letter"}
                    </button>
                </form>
            )}

            <div className="flex flex-wrap items-start gap-6">
                <div className="h-[600px] w-[750px]">
                    {letters && letters.length > 0 ? (
                        <SortTableLetters
                            lettersData={letters}
                            selectedLetterId={currentLetter?.id}
                            onSelectLetter={handleSelectLetter}
                        />
                    ) : (
                        <p className="text-sm italic">No letters yet. Sync from claims or add one manually.</p>
                    )}
                </div>

                {currentLetter && (
                    <div className="w-[380px] rounded-2xl bg-white/70 p-5 shadow-md">
                        <div className="mb-3 flex items-center justify-between">
                            <span className="text-xs font-semibold text-plum-500">
                                Letter {currentIndex + 1} of {letters.length}
                            </span>
                            <div className="flex items-center gap-1">
                                <IconButton size="small" onClick={handlePrev} disabled={currentIndex === 0}>
                                    <ArrowBackIosNewIcon fontSize="inherit" />
                                </IconButton>
                                <IconButton size="small" onClick={handleNext} disabled={currentIndex === letters.length - 1}>
                                    <ArrowForwardIosIcon fontSize="inherit" />
                                </IconButton>
                            </div>
                        </div>

                        <div className="mb-3 flex items-center justify-between">
                            <h3 className="text-lg font-bold text-plum-500">
                                {currentLetter.guest}
                                {currentLetter.partner ? ` & ${currentLetter.partner}` : ""}
                            </h3>
                            <Chip
                                size="small"
                                label={statusDraft}
                                color={STATUS_CHIP_COLOR[statusDraft] || "default"}
                            />
                        </div>

                        <div className="mb-3 flex flex-col gap-1 rounded-xl bg-cream-400/60 p-3 text-sm">
                            {currentLetter.gifts.map((g, i) => (
                                <div key={i} className="flex items-center gap-2">
                                    <CardGiftcardIcon fontSize="small" className="text-terracotta-500" />
                                    <span>
                                        {g.gift}{g.brand ? ` (${g.brand})` : ""}
                                        {g.price_cents ? ` — ${formatPriceCents(g.price_cents)}` : ""}
                                    </span>
                                </div>
                            ))}
                        </div>

                        <div className="mb-4 flex flex-col gap-1 text-sm text-gray-700">
                            <div className="flex items-start gap-2">
                                <LocalShippingIcon fontSize="small" className="mt-0.5 text-plum-500" />
                                <span>
                                    {currentLetter.street} {currentLetter.second_line}<br />
                                    {currentLetter.city}, {currentLetter.state_loc} {currentLetter.zipcode}<br />
                                    {currentLetter.country}
                                </span>
                            </div>
                            {currentLetter.phone && (
                                <div className="flex items-center gap-2">
                                    <PhoneIcon fontSize="small" className="text-plum-500" />
                                    <span>{currentLetter.phone}</span>
                                </div>
                            )}
                        </div>

                        <div className="mb-3">
                            <label htmlFor="letter-status" className="mb-1 block text-xs font-semibold text-plum-500">
                                Status
                            </label>
                            <Select
                                id="letter-status"
                                size="small"
                                fullWidth
                                value={statusDraft}
                                onChange={(e) => setStatusDraft(e.target.value)}
                            >
                                {STATUS_OPTIONS.map((option) => (
                                    <MenuItem key={option} value={option}>{option}</MenuItem>
                                ))}
                            </Select>
                        </div>

                        <TextField
                            multiline
                            fullWidth
                            minRows={8}
                            label="Letter body"
                            value={bodyDraft}
                            onChange={(e) => setBodyDraft(e.target.value.slice(0, LETTER_BODY_MAX_CHARS))}
                            inputProps={{ maxLength: LETTER_BODY_MAX_CHARS }}
                            helperText={`${bodyDraft.length}/${LETTER_BODY_MAX_CHARS}`}
                            FormHelperTextProps={{ sx: { textAlign: "right" } }}
                        />

                        {currentLetter.partner && currentLetter.source === "SYNC" && (
                            <button
                                type="button"
                                onClick={() => setDisjoinDialogOpen(true)}
                                disabled={isDisjoining}
                                className="mt-3 flex w-full items-center justify-center gap-2 rounded-full border border-plum-500 px-4 py-2 text-sm font-semibold text-plum-500 transition hover:bg-plum-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                <CallSplitIcon fontSize="small" />
                                Disjoin pair
                            </button>
                        )}

                        <div className="mt-4 flex items-center justify-between">
                            <button
                                type="button"
                                onClick={handleSave}
                                disabled={isSaving}
                                className="rounded-full bg-plum-500 px-5 py-2 text-sm font-semibold text-cream-400 shadow-sm transition hover:bg-plum-500/80 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                {isSaving ? "Saving..." : "Save"}
                            </button>
                            <IconButton
                                aria-label="Delete letter"
                                onClick={() => setDeleteDialogOpen(true)}
                                disabled={isDeleting}
                                className="!text-terracotta-500"
                            >
                                <DeleteOutlineIcon />
                            </IconButton>
                        </div>
                    </div>
                )}
            </div>

            <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
                <DialogTitle>Delete this letter?</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        This will permanently remove the letter for {currentLetter?.guest}
                        {currentLetter?.gifts?.length
                            ? ` (${currentLetter.gifts.map((g) => g.gift).join(', ')})`
                            : ""}
                        . This cannot be undone.
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
                    <Button onClick={handleDeleteConfirmed} color="error" disabled={isDeleting}>
                        {isDeleting ? "Deleting..." : "Delete"}
                    </Button>
                </DialogActions>
            </Dialog>

            <Dialog open={disjoinDialogOpen} onClose={() => setDisjoinDialogOpen(false)}>
                <DialogTitle>Disjoin this pair?</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        This splits the letter for {currentLetter?.guest}
                        {currentLetter?.partner ? ` & ${currentLetter.partner}` : ""} into
                        two separate letters, one per person, based on who actually claimed
                        each gift. It cannot be automatically re-merged by a future
                        "Sync from Claims" — undoing it requires editing the letters by hand.
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDisjoinDialogOpen(false)}>Cancel</Button>
                    <Button onClick={handleDisjoinConfirmed} color="primary" disabled={isDisjoining}>
                        {isDisjoining ? "Splitting..." : "Disjoin"}
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    );
}

export default LettersAdmin;
