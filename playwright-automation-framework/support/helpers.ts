import { readFileSync } from 'fs';
import { join } from 'path';

type ScreenElement = {
  intent: string;
  selector: string;
  tag: string;
  type: string;
  label: string | null;
  text: string | null;
  placeholder: string | null;
  visible: boolean;
  stability: string;
};

export type ScreenMap = {
  page: string;
  url: string;
  route?: string;
  build_id?: string | null;
  dom_fingerprint?: string;
  captured_at: string;
  elements: ScreenElement[];
};

export const loadScreenMap = (feature: string): ScreenMap => {
  const raw = readFileSync(
    join(__dirname, 'screen-maps', `${feature}.screen.json`),
    'utf-8',
  );
  return JSON.parse(raw) as ScreenMap;
};

export const getSelector = (map: ScreenMap, intent: string): string => {
  const matches = map.elements.filter((e) => e.intent === intent);
  if (!matches.length) {
    throw new Error(`No screen map entry for intent: "${intent}"`);
  }
  if (matches.length === 1) return matches[0].selector;
  throw new Error(
    `Ambiguous screen map intent "${intent}" with ${matches.length} matches`,
  );
};
