import ease from '../eases/pokerhand/index';
import { head } from './fns';

/**
 * 
 * @param {string[]} lines
 * @returns {number}
 */
const countPlayers = lines => {

    const holeCardsLineCount = lines.indexOf('*** HOLE CARDS ***');

    const seats = (v, i) => v.startsWith('Seat ') && i < holeCardsLineCount;

    return lines.filter(seats).length;

};

/**
 * 
 * @param {string[]} lines
 * @returns {number}
 */
const getButtonSeat = lines => {

    // Table 'Akiyama II' 6-max Seat #5 is the button

    const buttonLine = lines[1];

    const match = buttonLine.match(/\s#.\s/);

    return Number(match[0].replace('#', ''));
};

/**
 * 1-> Tornament Hold'em  
 * 2-> Cash Hold'em  
 * 3-> Tournament PLO  
 * 4-> Cash PLO
 * 
 * @param {string[]} lines
 * @returns {number}
 */
const getGameMode = lines => {

    // cash
    // PokerStars Hand #206007550592:  Hold'em No Limit (€0.01/€0.02 EUR) - ...

    const gameModeLine = lines[0];

    const tournament = gameModeLine.includes('Tournament');
    const Holdem = gameModeLine.includes('Hold');

    if (tournament) return Holdem ? 1 : 3;
    else return Holdem ? 2 : 4;
};

/**
 * 
 * @param {string[]} lines 
 * @param {number} index
 * @param {number} count 
 */
export default function (lines, index, count) {

    const gameMode = getGameMode(lines);

    const buttonSeat = getButtonSeat(lines);

    const mainInfo = ease.createMainInfo(lines, index, count);

    const players = ease.createPlayers(lines, buttonSeat, gameMode);

    const histories = ease.createHistories(lines, players);

    const handsListItem = ease.createHandsListItem(players, histories, mainInfo);

    return {

        playersCount: countPlayers(lines),
        buttonSeat,
        gameMode,
        mainInfo,
        players,
        histories,
        handsListItem,
        lines,
        index
    };
}

export const testables = {
    getButtonSeat,
    getGameMode,
}