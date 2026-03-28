import { Theme, Container } from './types';

const injectedTheme: string = 'light';
const injectedContainer: string = 'none';

let theme: Theme = 'light';
let container: Container = 'none';

if (injectedTheme === 'light' || injectedTheme === 'dark') {
  theme = injectedTheme;
}
if (injectedContainer === 'centered' || injectedContainer === 'none') {
  container = injectedContainer;
}

export default {
  theme,
  container,
};
