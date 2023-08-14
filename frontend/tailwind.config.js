/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				primary: {
					100: '#f9dfdf',
					200: '#f3bebe',
					300: '#ed9e9e',
					400: '#e77d7d',
					500: '#e15d5d',
					600: '#b44a4a',
					700: '#873838',
					800: '#5a2525',
					900: '#2d1313'
				},

				secondary: {
					100: '#e9f3ff',
					200: '#d4e8fe',
					300: '#bedcfe',
					400: '#a9d1fd',
					500: '#93c5fd',
					600: '#769eca',
					700: '#587698',
					800: '#3b4f65',
					900: '#1d2733'
				},

				accent: '#fbbf24',

				neutral: '#e7e5e4',

				'base-100': '#f1f2f3',

				info: '#d1d5db',

				success: '#22c55e',

				warning: '#facc15',

				error: '#f87171'
			}
		}
	},
	plugins: [require('daisyui')],
	daisyui: {
		themes: [
			{
				mytheme: {
					primary: '#E15D5D',

					secondary: '#93c5fd',

					accent: '#fbbf24',

					neutral: '#e7e5e4',

					'base-100': '#f1f2f3',

					info: '#d1d5db',

					success: '#22c55e',

					warning: '#facc15',

					error: '#f87171'
				}
			}
		]
	}
};
