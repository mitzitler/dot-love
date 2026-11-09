import * as React from 'react';
import { ToggleButton, ToggleButtonGroup } from '@mui/material';

// Who should write a letter. Mirrors LETTER_ASSIGNEES in the miatun lambda;
// letters without one are treated as EITHER.
export type Assignee = 'MITZI' | 'MATTHEW' | 'EITHER';

export const DEFAULT_ASSIGNEE: Assignee = 'EITHER';

export const ASSIGNEE_OPTIONS: readonly {
    value: Assignee;
    label: string;
    short: string;
    color: string;
}[] = [
    { value: 'MITZI', label: 'Mitzi', short: 'Mi', color: '#DE6B54' },
    { value: 'MATTHEW', label: 'Matthew', short: 'Ma', color: '#902E6B' },
    { value: 'EITHER', label: 'Either', short: 'Ei', color: '#6b7280' },
];

export function assigneeOf(letter: { assignee?: string | null }): Assignee {
    const value = letter.assignee as Assignee;
    return ASSIGNEE_OPTIONS.some((o) => o.value === value) ? value : DEFAULT_ASSIGNEE;
}

/**
 * Segmented Mitzi / Matthew / Either control. Exactly one segment is always
 * selected; clicking the selected one does nothing. `compact` renders the
 * two-letter labels used in the letters table.
 */
function LetterAssigneeToggle({
    value,
    onChange,
    compact = false,
    guest = '',
}: {
    value: Assignee;
    onChange: (value: Assignee) => void;
    compact?: boolean;
    guest?: string;
}) {
    return (
        <ToggleButtonGroup
            exclusive
            size="small"
            value={value}
            fullWidth={!compact}
            // Clicking in a table row shouldn't also select the row.
            onClick={(e) => e.stopPropagation()}
            onChange={(_e, next: Assignee | null) => {
                if (next && next !== value) onChange(next);
            }}
            aria-label={guest ? `Who writes the letter for ${guest}` : 'Who writes this letter'}
        >
            {ASSIGNEE_OPTIONS.map((option) => (
                <ToggleButton
                    key={option.value}
                    value={option.value}
                    aria-label={`For ${option.label}${guest ? `: ${guest}` : ''}`}
                    title={`For ${option.label}`}
                    sx={{
                        textTransform: 'none',
                        lineHeight: 1.2,
                        fontWeight: 600,
                        fontSize: compact ? '10px' : '13px',
                        padding: compact ? '1px 5px' : '4px 8px',
                        minWidth: compact ? 0 : undefined,
                        color: option.color,
                        borderColor: `${option.color}66`,
                        backgroundColor: 'rgba(255, 255, 255, 0.6)',
                        '&:hover': { backgroundColor: `${option.color}1f` },
                        '&.Mui-selected, &.Mui-selected:hover': {
                            color: '#FBFBF2',
                            backgroundColor: option.color,
                        },
                    }}
                >
                    {compact ? option.short : option.label}
                </ToggleButton>
            ))}
        </ToggleButtonGroup>
    );
}

export default React.memo(LetterAssigneeToggle);
