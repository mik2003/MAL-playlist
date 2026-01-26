export function createArray(n: number): number[] {
    return Array.from({ length: n }, (_, i) => i);
}

export function shuffleArray<T>(array: T[]): T[] {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

export function scrollParentToChild(parent: HTMLElement, child: HTMLElement): void {
    const parentRect = parent.getBoundingClientRect();
    const parentViewableArea = { height: parent.clientHeight };
    const childRect = child.getBoundingClientRect();

    const isViewable =
        childRect.top >= parentRect.top &&
        childRect.bottom <= parentRect.top + parentViewableArea.height;

    if (!isViewable) {
        const scrollTop = childRect.top - parentRect.top;
        const scrollBot = childRect.bottom - parentRect.bottom;
        parent.scrollTop += Math.abs(scrollTop) < Math.abs(scrollBot) ? scrollTop : scrollBot;
    }
}
