import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
    Button,
    Checkbox,
    Chip,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    FormControlLabel,
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
import LetterAssigneeToggle, { ASSIGNEE_OPTIONS, assigneeOf } from "./LetterAssigneeToggle";
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

// Storage cap on the letter body; mirrors LETTER_BODY_MAX_CHARS in the
// miatun lambda, which rejects longer bodies on save.
export const LETTER_BODY_MAX_CHARS = 500;

// The card's sign-off (SSM /dot-love/handwrytten/wishes). Handwrytten counts
// it toward the same 500-char limit as the body, so a sendable body is
// shorter. Keep in sync with SSM; the lambda computes the same number in
// letter_body_send_max_chars and /send rejects anything longer.
const LETTER_SIGN_OFF = "With love, Mitzi & Matthew";
export const LETTER_BODY_SEND_MAX_CHARS = LETTER_BODY_MAX_CHARS - LETTER_SIGN_OFF.length;

// How long typing must pause before the letter body autosaves. Status
// changes save immediately.
const AUTOSAVE_DELAY_MS = 1000;

const SAVE_STATE_LABEL = {
    saved: "All changes saved",
    unsaved: "Unsaved changes...",
    saving: "Saving...",
    error: "Save failed",
};

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

// Quick filters above the letters table: everything, or one assignee.
const ASSIGNEE_FILTERS = [
    { value: "ALL", label: "All", color: "#374151" },
    ...ASSIGNEE_OPTIONS,
];

function matchesAssigneeFilter(letter, filter) {
    return filter === "ALL" || assigneeOf(letter) === filter;
}

/**
 * Status + body editor for one letter, autosaving as you go. Rendered with
 * key={letter.id}, so drafts load once per letter and a save response
 * landing mid-typing can't clobber newer text. Any pending edit is flushed
 * when the editor unmounts (switching letters, leaving the tab), and the
 * browser warns before closing the page with unsaved changes.
 */
function LetterDraftEditor({ letter, saveDraft, flushRef }) {
    const [bodyDraft, setBodyDraft] = useState(letter.letter_body || "");
    const [statusDraft, setStatusDraft] = useState(letter.status || "DRAFT");
    const [saveState, setSaveState] = useState("saved");
    const overBy = bodyDraft.length - LETTER_BODY_SEND_MAX_CHARS;

    // savedRef: the last draft sent to the server (in flight or done).
    const savedRef = useRef({ letter_body: bodyDraft, status: statusDraft });
    const draftRef = useRef(savedRef.current);
    draftRef.current = { letter_body: bodyDraft, status: statusDraft };
    const timerRef = useRef(null);
    const inFlightRef = useRef(0);

    const flush = useCallback(() => {
        clearTimeout(timerRef.current);
        timerRef.current = null;
        const draft = draftRef.current;
        if (
            draft.letter_body === savedRef.current.letter_body &&
            draft.status === savedRef.current.status
        ) {
            return;
        }
        savedRef.current = draft;
        inFlightRef.current += 1;
        setSaveState("saving");
        saveDraft(letter.id, draft)
            .then(() => {
                if (savedRef.current === draft) setSaveState("saved");
            })
            .catch((err) => {
                console.error("Failed to autosave letter:", err);
                // Only the newest save decides the indicator; a stale
                // failure is superseded by the full-body save after it.
                if (savedRef.current === draft) {
                    savedRef.current = {};
                    setSaveState("error");
                    toast.error("Failed to save letter. Your text is still here.", toastOptions);
                }
            })
            .finally(() => {
                inFlightRef.current -= 1;
            });
    }, [letter.id, saveDraft]);

    useEffect(() => {
        const saved = savedRef.current;
        if (bodyDraft === saved.letter_body && statusDraft === saved.status) {
            // Edited back to what's already saved: nothing left to send.
            clearTimeout(timerRef.current);
            setSaveState((state) => (state === "unsaved" ? "saved" : state));
            return;
        }
        setSaveState("unsaved");
        clearTimeout(timerRef.current);
        const delay = statusDraft !== saved.status ? 0 : AUTOSAVE_DELAY_MS;
        timerRef.current = setTimeout(flush, delay);
    }, [bodyDraft, statusDraft, flush]);

    // Save anything pending when leaving this letter, and let the parent
    // force a save before actions that re-key letters (sync, disjoin).
    useEffect(() => {
        flushRef.current = flush;
        return () => {
            flushRef.current = null;
            flush();
        };
    }, [flush, flushRef]);

    useEffect(() => {
        const warnIfUnsaved = (e) => {
            const dirty =
                draftRef.current.letter_body !== savedRef.current.letter_body ||
                draftRef.current.status !== savedRef.current.status;
            if (!dirty && inFlightRef.current === 0) return;
            flush();
            e.preventDefault();
            e.returnValue = "";
        };
        window.addEventListener("beforeunload", warnIfUnsaved);
        return () => window.removeEventListener("beforeunload", warnIfUnsaved);
    }, [flush]);

    return (
        <>
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
                // Over-length text stays editable (and keeps autosaving) so
                // older letters can be trimmed down; only sending is blocked.
                onChange={(e) => setBodyDraft(e.target.value.slice(0, LETTER_BODY_MAX_CHARS))}
                inputProps={{ maxLength: LETTER_BODY_MAX_CHARS }}
                error={overBy > 0}
                helperText={
                    overBy > 0
                        ? `${bodyDraft.length}/${LETTER_BODY_SEND_MAX_CHARS} · ${overBy} too long to fit on the card with the sign-off`
                        : `${bodyDraft.length}/${LETTER_BODY_SEND_MAX_CHARS}`
                }
                FormHelperTextProps={{ sx: { textAlign: "right" } }}
            />

            <div className="mt-1 flex items-center gap-2 text-xs">
                <span className={saveState === "error" ? "font-semibold text-terracotta-500" : "text-gray-500"}>
                    {SAVE_STATE_LABEL[saveState]}
                </span>
                {saveState === "error" && (
                    <button
                        type="button"
                        onClick={flush}
                        className="font-semibold text-plum-500 underline"
                    >
                        Retry
                    </button>
                )}
            </div>
        </>
    );
}

export function LettersAdmin({ letters, setLetters, apiKey, triggerGetAllLetters }) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [showNewLetterForm, setShowNewLetterForm] = useState(false);
    const [newLetterForm, setNewLetterForm] = useState(EMPTY_NEW_LETTER);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [disjoinDialogOpen, setDisjoinDialogOpen] = useState(false);
    const [assigneeFilter, setAssigneeFilter] = useState("ALL");

    const [syncLetters, { isLoading: isSyncing }] = useSyncLettersMutation();
    const [createLetter, { isLoading: isCreating }] = useCreateLetterMutation();
    const [updateLetter] = useUpdateLetterMutation();
    const [deleteLetter, { isLoading: isDeleting }] = useDeleteLetterMutation();
    const [disjoinLetterPair, { isLoading: isDisjoining }] = useDisjoinLetterPairMutation();

    const currentLetter = letters && letters.length > 0 ? letters[currentIndex] : null;

    // The table and prev/next only cover letters matching the filter. The
    // open letter stays open even if it's reassigned out of the filter, so
    // the editor isn't yanked away mid-edit.
    const visibleLetters = useMemo(
        () => (letters || []).filter((letter) => matchesAssigneeFilter(letter, assigneeFilter)),
        [letters, assigneeFilter]
    );
    const visiblePos = currentLetter
        ? visibleLetters.findIndex((letter) => letter.id === currentLetter.id)
        : -1;
    const assigneeCounts = useMemo(() => {
        const counts = { ALL: (letters || []).length };
        for (const letter of letters || []) {
            const assignee = assigneeOf(letter);
            counts[assignee] = (counts[assignee] || 0) + 1;
        }
        return counts;
    }, [letters]);

    // PATCH reads the whole letter and writes every field back, so two
    // overlapping updates to one letter could undo each other. Chain them
    // so they reach the server one at a time, in order.
    const updateChainRef = useRef(Promise.resolve());
    const editorFlushRef = useRef(null);
    const deletedIdsRef = useRef(new Set());

    const enqueueUpdate = useCallback((letterId, updates) => {
        const run = updateChainRef.current.then(() =>
            updateLetter({ apiKey, letterId, updates }).unwrap()
        );
        updateChainRef.current = run.catch(() => {});
        return run.then((result) => {
            // Merge only the fields this update sent, so a response can't
            // revert a newer optimistic change (e.g. a checkbox click
            // queued behind a body save).
            setLetters((prev) =>
                prev.map((letter) =>
                    letter.id === letterId
                        ? { ...letter, ...updates, updated_at: result.letter.updated_at }
                        : letter
                )
            );
            return result;
        });
    }, [apiKey, updateLetter, setLetters]);

    const saveDraft = useCallback((letterId, draft) => {
        // The editor flushes on unmount, including right after a delete.
        if (deletedIdsRef.current.has(letterId)) return Promise.resolve();
        return enqueueUpdate(letterId, draft);
    }, [enqueueUpdate]);

    const flushPendingSaves = async () => {
        editorFlushRef.current?.();
        await updateChainRef.current;
    };

    const handleToggleAddressConfirmed = useCallback((letter) => {
        const confirmed = !letter.address_confirmed;
        const setConfirmed = (value) =>
            setLetters((prev) =>
                prev.map((l) => (l.id === letter.id ? { ...l, address_confirmed: value } : l))
            );
        setConfirmed(confirmed);
        enqueueUpdate(letter.id, { address_confirmed: confirmed }).catch((err) => {
            console.error("Failed to update address confirmation:", err);
            setConfirmed(!confirmed);
            toast.error(`Failed to update address confirmation for ${letter.guest}.`, toastOptions);
        });
    }, [enqueueUpdate, setLetters]);

    const handleSetAssignee = useCallback((letter, assignee) => {
        const previous = assigneeOf(letter);
        if (assignee === previous) return;
        const setAssignee = (value) =>
            setLetters((prev) =>
                prev.map((l) => (l.id === letter.id ? { ...l, assignee: value } : l))
            );
        setAssignee(assignee);
        enqueueUpdate(letter.id, { assignee }).catch((err) => {
            console.error("Failed to update letter assignee:", err);
            setAssignee(previous);
            toast.error(`Failed to update who writes the letter for ${letter.guest}.`, toastOptions);
        });
    }, [enqueueUpdate, setLetters]);

    const selectLetterById = (letterId) => {
        const index = (letters || []).findIndex((letter) => letter.id === letterId);
        if (index !== -1) setCurrentIndex(index);
    };

    const handleFilterChange = (filter) => {
        setAssigneeFilter(filter);
        if (currentLetter && matchesAssigneeFilter(currentLetter, filter)) return;
        const firstMatch = (letters || []).find((letter) => matchesAssigneeFilter(letter, filter));
        if (firstMatch) selectLetterById(firstMatch.id);
    };

    useEffect(() => {
        if (letters && currentIndex >= letters.length) {
            setCurrentIndex(Math.max(0, letters.length - 1));
        }
    }, [letters, currentIndex]);

    const handleSync = async () => {
        try {
            await flushPendingSaves();
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

    const handleDeleteConfirmed = async () => {
        if (!currentLetter) return;
        const letterId = currentLetter.id;
        deletedIdsRef.current.add(letterId);
        try {
            await deleteLetter({ apiKey, letterId }).unwrap();
            const updatedLetters = letters.filter((letter) => letter.id !== letterId);
            setLetters(updatedLetters);
            setCurrentIndex((index) => Math.max(0, Math.min(index, updatedLetters.length - 1)));
            toast.success("Letter deleted.", toastOptions);
        } catch (err) {
            deletedIdsRef.current.delete(letterId);
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
            // Disjoin re-keys the letter and carries over the saved body,
            // so get any pending edit to the server first.
            await flushPendingSaves();
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

    // Step through the filtered list. If the open letter has been filtered
    // out, either arrow jumps to the first visible letter.
    const handlePrev = () => {
        const target = visiblePos === -1 ? visibleLetters[0] : visibleLetters[visiblePos - 1];
        if (target) selectLetterById(target.id);
    };
    const handleNext = () => {
        const target = visiblePos === -1 ? visibleLetters[0] : visibleLetters[visiblePos + 1];
        if (target) selectLetterById(target.id);
    };
    const filterLabel = ASSIGNEE_FILTERS.find((f) => f.value === assigneeFilter)?.label;

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

            {letters && letters.length > 0 && (
                <div className="mb-3 flex flex-wrap items-center gap-2" role="group" aria-label="Filter letters by who writes them">
                    <span className="text-xs font-semibold text-plum-500">Show:</span>
                    {ASSIGNEE_FILTERS.map((filter) => {
                        const selected = assigneeFilter === filter.value;
                        return (
                            <Chip
                                key={filter.value}
                                size="small"
                                clickable
                                label={`${filter.label} · ${assigneeCounts[filter.value] || 0}`}
                                onClick={() => handleFilterChange(filter.value)}
                                aria-pressed={selected}
                                variant={selected ? "filled" : "outlined"}
                                sx={{
                                    fontWeight: 600,
                                    borderColor: filter.color,
                                    color: selected ? "#FBFBF2" : filter.color,
                                    backgroundColor: selected ? filter.color : "rgba(255, 255, 255, 0.6)",
                                    "&&:hover": {
                                        backgroundColor: selected ? filter.color : `${filter.color}1f`,
                                    },
                                }}
                            />
                        );
                    })}
                </div>
            )}

            <div className="flex flex-wrap items-start gap-6">
                <div className="h-[600px] w-[750px]">
                    {!letters || letters.length === 0 ? (
                        <p className="text-sm italic">No letters yet. Sync from claims or add one manually.</p>
                    ) : visibleLetters.length === 0 ? (
                        <p className="text-sm italic">No letters for {filterLabel}.</p>
                    ) : (
                        <SortTableLetters
                            lettersData={visibleLetters}
                            selectedLetterId={currentLetter?.id}
                            onSelectLetter={handleSelectLetter}
                            onToggleAddressConfirmed={handleToggleAddressConfirmed}
                            onSetAssignee={handleSetAssignee}
                        />
                    )}
                </div>

                {currentLetter && (
                    <div className="w-[380px] rounded-2xl bg-white/70 p-5 shadow-md">
                        <div className="mb-3 flex items-center justify-between">
                            <span className="text-xs font-semibold text-plum-500">
                                {visiblePos !== -1
                                    ? `Letter ${visiblePos + 1} of ${visibleLetters.length}`
                                    : `Not in "${filterLabel}"`}
                                {assigneeFilter !== "ALL" && visiblePos !== -1 ? ` (${filterLabel})` : ""}
                            </span>
                            <div className="flex items-center gap-1">
                                <IconButton
                                    size="small"
                                    onClick={handlePrev}
                                    disabled={visibleLetters.length === 0 || visiblePos === 0}
                                >
                                    <ArrowBackIosNewIcon fontSize="inherit" />
                                </IconButton>
                                <IconButton
                                    size="small"
                                    onClick={handleNext}
                                    disabled={visibleLetters.length === 0 || visiblePos === visibleLetters.length - 1}
                                >
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
                                label={currentLetter.status}
                                color={STATUS_CHIP_COLOR[currentLetter.status] || "default"}
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
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        size="small"
                                        checked={!!currentLetter.address_confirmed}
                                        onChange={() => handleToggleAddressConfirmed(currentLetter)}
                                    />
                                }
                                label="Address confirmed"
                                componentsProps={{ typography: { fontSize: "0.875rem" } }}
                            />
                        </div>

                        <div className="mb-3">
                            <span className="mb-1 block text-xs font-semibold text-plum-500">For</span>
                            <LetterAssigneeToggle
                                value={assigneeOf(currentLetter)}
                                guest={currentLetter.guest}
                                onChange={(value) => handleSetAssignee(currentLetter, value)}
                            />
                        </div>

                        <LetterDraftEditor
                            key={currentLetter.id}
                            letter={currentLetter}
                            saveDraft={saveDraft}
                            flushRef={editorFlushRef}
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

                        <div className="mt-4 flex items-center justify-end">
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
