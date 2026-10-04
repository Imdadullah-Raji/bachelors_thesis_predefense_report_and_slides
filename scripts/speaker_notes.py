"""Speaker notes for the predefense talk: one source for the .pptx notes pane and
the printed A4 notes (slides/speaker_notes.pdf).

Text is from slides_mds/*.md with light grammar corrections only.
Markup inside the strings:
    [[...]]  stage direction (pointing cue)      -> italic in the PDF
    {{...}}  text Claude drafted where the .md had none -> marked in both outputs

    conda run -n talkbuild python scripts/speaker_notes.py      # writes the PDF
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (key, slide title, estimated time or '', [paragraphs]) in deck order
NOTES = [
    ('cover', 'Cover', '', [
        '{{Good morning. I am Imdadullah Raji, and together with Abdullah Al Mamun, under the '
        'supervision of Dr Md Ali, I will present our thesis: Modeling and Control of Unsteady Flows '
        'over Rapidly Maneuvering Airfoils at Ultra-Low Reynolds Number.}}',
    ]),
    ('opening', 'Opening quote', '', [
        'The Navier–Stokes equations give us the highest-fidelity representation of fluid flows. However, '
        'they give us surprisingly little insight into the flow physics in question. As Feynman asks, '
        '“could we predict the auroras?”',
        'The question that concerns us here is: could we see the vortices roll up like that just by looking '
        'at the equations? No, but we can indeed calculate them, like this animation, which came out of a '
        'calculation that took 2 hours on 6 cores.',
    ]),
    ('rom', 'Objective: Reduced-Order Models', '', [
        'However, we can only afford fractions of a millisecond when it comes to active flow control. '
        'Therefore, the goal is to obtain a simplified model. One way to do this is to resolve the flow into '
        'patterns observed in space. Proper orthogonal decomposition, shown here, is one such technique. It '
        'describes the flow as a sum of its most energetic modes. The simulation data takes gigabytes on our '
        'computers, but this POD takes only about 12 megabytes, and a fraction of a millisecond to compute: '
        '19 µs on a single core of my machine, to be exact.',
    ]),
    ('control', 'Objective: Model-Based Active Flow Control', '', [
        'After reducing the flow to a smaller state vector x, we need a model for how those variables evolve '
        'under actuation: the f. [[Point to the board.]]',
        'We first investigate whether a simple linear model is sufficient. [[Point to the linear equation.]]',
        'As the dynamics are in fact nonlinear, we can expect that to fail. Then nonlinear '
        'system-identification tools can be employed.',
        'For example, Sparse Identification of Nonlinear Dynamics, or SINDy for short, identifies a nonlinear '
        'model directly from simulation data. The ultimate purpose is to obtain a controller that maps the '
        'state x to an actuation u. [[Again point to the relevant equation.]]',
    ]),
    ('solver', 'Numerical Solver', '20 s', [
        'The simulations were conducted in the open-source finite-volume code OpenFOAM. The problem concerns '
        'unsteady fluid flows at low Reynolds number. The flow is laminar, hence the smallest scale to resolve '
        'is the boundary-layer thickness δ. We solve the Navier–Stokes equations directly, without any '
        'turbulence model. The flow is also assumed to be incompressible. Second-order schemes were used for '
        'both convection and time stepping.',
    ]),
    ('mesh', 'Computational Mesh', '25 s', [
        'The simulation domain is a disk with a radius of 30 chord lengths. When the angle of attack needs '
        'changing, we rotate the freestream instead of the airfoil. The first-layer height is taken to be '
        'approximately one hundredth of the Blasius flat-plate boundary-layer thickness. Together with the '
        'growth rate, it ensures that the boundary layer is resolved by approximately 40 cells.',
    ]),
    ('ale', 'Pitching Motion: ALE Formulation', '', [
        'The pitch motion is handled by rotating the entire mesh relative to the freestream. This introduces '
        'an additional convective term in every cell, due to the mesh motion. [[Point to u_m.]] This numerical '
        'technique is called the Arbitrary Lagrangian–Eulerian method, as it solves the Eulerian Navier–Stokes '
        'equations with an arbitrary Lagrangian motion of the cells.',
    ]),
    ('wake', 'Wake Patterns at Ultra-Low Reynolds Number', '', [
        'The violent mixing of turbulent flow is absent in laminar flows at low Reynolds number. As a result, '
        'large vortices can survive for a long time without breaking up into smaller ones. In this regime, the '
        'shear layer is thick, the wake is broad, and large vortices interact with each other to produce such '
        'intricate flow structures. This structure was studied computationally by Kurtuluş. She studied a '
        'NACA0012 airfoil and classified the observed flow structures into five modes according to the wake '
        'vorticity pattern.',
        'First, the attached flow. Second, a von Kármán-like vortex street. Third, the alternating vortex-pair '
        'shedding mode. Fourth, alternate vortex with single vortex shedding. Fifth, bluff-body vortex shedding.',
        '{{Our own simulations at Re = 500 reproduce mode 2 at α = 14° and mode 3 at α = 26°.}} '
        '[[Point to the two videos.]]',
    ]),
    ('durante', 'Period Doubling, Tripling and Chaos', '', [
        'Looking at the force histories also reveals the temporal pattern. Durante et al. looked at the time '
        'series of the force coefficients at Re = 1000, their phase portraits and their Fourier amplitudes.',
        'Initially the force peaks are single, and the phase portrait is a single loop. Then, near α = 22°, '
        'the signal transitions into alternating small and large peaks, and the phase portrait contains two '
        'loops. The Fourier spectrum develops an amplitude at the subharmonic.',
        'Additionally, period-three and aperiodic, chaotic flows are also observed.',
    ]),
    ('spanwise', 'Beyond 2D: Spanwise Instability', '', [
        'In reality, a 3D spanwise instability develops, in the same way that the symmetric wake of a cylinder '
        'goes unsteady and develops the von Kármán vortex street.',
        'This instability develops as corrugations of different wavelengths in the spanwise direction. The '
        'photo here is from Williamson’s 1996 review paper on the vortex dynamics of the cylinder wake. '
        '[[Point to the photos.]]',
        'Gupta et al. investigated the 3D instability at Re = 1000 through numerical studies and water-channel '
        'experiments. They observed instability mechanisms similar to those of cylinder wakes. They found that '
        'the onset of the 3D instability varies as the inverse square root of the Reynolds number, which sits '
        'before all the period-doubling bifurcations reported in 2D simulations.',
    ]),
    ('lev', 'Pitching Airfoil and the Leading-Edge Vortex', '', [
        '{{When the airfoil pitches up rapidly, the lift has two sources. The first is added-mass, or '
        'non-circulatory, lift: the airfoil has to accelerate the fluid around it, so this part appears only '
        'while the pitch rate and acceleration are non-zero, the spikes at the start and end of the ramp in the '
        'video.}} [[Point to the added-mass equation and the α̇, α̈ graphs.]]',
        '{{The second is circulatory lift, set by the circulation through the Kutta–Joukowski theorem, L′ = '
        'ρUΓ. During the ramp a leading-edge vortex rolls up and stays over the suction side, adding '
        'circulation and therefore lift. Once the motion stops, the vortex detaches and convects downstream, '
        'and the lift falls.}}',
        '{{Eldredge and Jones show the effect of pitch rate on a flat plate: the faster the manoeuvre, the '
        'tighter and stronger the leading-edge vortex, and the higher the lift peak, from about 3 at K = 0.1 '
        'to about 16 at K = 1.}} [[Point to the figure.]]',
    ]),
    ('resources', 'Books Consulted and Code', '', [
        '{{These are the books we consulted. The code developed for this work is available in these two '
        'repositories.}}',
    ]),
    ('qna', 'Questions?', '', [
        '{{Thank you for your attention. We are happy to take your questions.}}',
    ]),
]
BY_KEY = {k: (title, time, paras) for k, title, time, paras in NOTES}


def pptx_text(key):
    """Plain text for the PowerPoint notes pane."""
    title, time, paras = BY_KEY[key]
    out = []
    for p in paras:
        p = re.sub(r'\[\[(.*?)\]\]', r'(\1)', p)
        p = re.sub(r'\{\{(.*?)\}\}', r'[drafted] \1', p)
        out.append(p)
    return (f'(est. {time})\n' if time else '') + '\n'.join(out)


# ------------------------------------------------------------------ PDF
UNICODE = {
    'α̇': r'$\dot\alpha$', 'α̈': r'$\ddot\alpha$', 'α': r'$\alpha$', '°': r'$^\circ$', 'µ': r'$\mu$',
    'δ': r'$\delta$', 'ρ': r'$\rho$', 'Γ': r'$\Gamma$', 'L′': r"$L'$", 'ş': r'\c{s}', 'á': r"\'a",
    '–': '--', '“': '``', '”': "''", '’': "'", 'u_m': r'$\mathbf{u}_m$', '&': r'\&', '%': r'\%',
}


def to_latex(p):
    for k, v in UNICODE.items():
        p = p.replace(k, v)
    p = p.replace('et al. ', 'et al.\\ ').replace(' = ', '~=~')
    p = re.sub(r'\[\[(.*?)\]\]', r'\\cue{\1}', p)
    p = re.sub(r'\{\{(.*?)\}\}', r'\\drafted{\1}', p)
    return p


def write_pdf():
    out = ROOT / 'slides'
    body = []
    for n, (key, title, time, paras) in enumerate(NOTES, start=1):
        head = rf'\slide{{{n}}}{{{to_latex(title)}}}{{{time}}}'
        body.append(head + '\n' + '\n\n'.join(to_latex(p) for p in paras))
    tex = r'''\documentclass[12pt,a4paper]{article}
\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage[margin=22mm]{geometry}
\usepackage{amsmath,bm,xcolor,titlesec,fancyhdr}
\definecolor{ink}{RGB}{31,42,68}\definecolor{accent}{RGB}{139,30,45}\definecolor{draft}{RGB}{22,86,140}
\setlength{\parindent}{0pt}\setlength{\parskip}{7pt}\linespread{1.25}
\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}
\fancyfoot[L]{\small\color{ink!70}Thesis predefense: speaker notes}\fancyfoot[R]{\small\color{ink!70}\thepage}
\newcommand{\cue}[1]{{\itshape\color{accent}[#1]}}
\newcommand{\drafted}[1]{{\color{draft}#1}}
\newcommand{\slide}[3]{\par\vspace{10pt}\noindent{\large\bfseries\color{ink}Slide #1\quad #2}\hfill{\small\color{ink!70}#3}\par
  \vspace{-4pt}{\color{accent}\rule{\linewidth}{0.6pt}}\par}
\begin{document}\color{ink}
{\LARGE\bfseries Speaker notes}\par\vspace{2pt}
{\color{ink!75}Modeling and Control of Unsteady Flows over Rapidly Maneuvering Airfoils at Ultra-Low Reynolds Number}\par
\vspace{6pt}{\small \cue{Italic in brackets}: pointing cues.\quad \drafted{Blue text}: drafted by Claude where the notes were empty.}\par
''' + '\n\n'.join(body) + '\n\\end{document}\n'
    (out / 'speaker_notes.tex').write_text(tex)
    for _ in range(2):
        subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'speaker_notes.tex'],
                       cwd=out, check=True, stdout=subprocess.DEVNULL)
    for ext in ('aux', 'log'):
        (out / f'speaker_notes.{ext}').unlink(missing_ok=True)
    print(out / 'speaker_notes.pdf')


if __name__ == '__main__':
    write_pdf()
