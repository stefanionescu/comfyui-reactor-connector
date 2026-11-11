import { fileURLToPath } from 'node:url';
const rulesFile = fileURLToPath(new URL('markdownlint.jsonc', import.meta.url));
export default {
    config: { extends: rulesFile },
    frontMatter: String.raw `^(?:(?:---[^\S\r\n]*\r?\n[\s\S]*?\r?\n---|\+\+\+[^\S\r\n]*\r?\n[\s\S]*?\r?\n(?:\+\+\+|\.\.\.)|\{[^\S\r\n]*\r?\n[\s\S]*?\r?\n\})[^\S\r\n]*(?:\r?\n|$))?(?:(?:[^\S\r\n]*\r?\n)*(?:import|export) [^\r\n]*(?:\r?\n[^\S\r\n]*\S[^\r\n]*)*(?:\r?\n|$))*`,
    noBanner: true,
    noProgress: true,
    outputFormatters: [
        [
            ({ results, logMessage }) => {
                logMessage(JSON.stringify(results));
            },
        ],
    ],
};
