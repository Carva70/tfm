% Documentación básica para CLS: https://es.overleaf.com/learn/latex/Writing_your_own_class
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{MUXLaTeX}[27/04/2023 - MUXLaTeX]
%%%%%%%%%%%%%%%%%%%%%%%%% <--- COMIENZO DE LA PLANTILLA

%%%%%%%%%%%%%%%%%%%%%%% <- COMIENZO C. GENERALES

\LoadClass[a4paper, 12pt, oneside, openany]{book} % quitar openany para empezar impar
\usepackage{hyperref}
\usepackage{mathpazo}
% Margin setup
\usepackage[headheight=10ex,inner=2.5cm,
	outer=2.5cm, % Outer margin
	bindingoffset=.5cm, % Binding offset
	top=2.5cm, % Top margin
	bottom=2cm]{geometry}
\usepackage{ifthen}
\usepackage{afterpage}
\usepackage{float}
\setlength{\parskip}{0.7em}

%\usepackage[document]{ragged2e}
\usepackage{todonotes}
%\usepackage{hyphenat}
%\hyphenpenalty=10000
\usepackage[spanish]{babel}
\usepackage{watermark}
\usepackage[most]{tcolorbox}
\newcommand{\digital}[1]{
        \ifthenelse{\equal{#1}{no}}{
        \newcommand{\cambio}{
        \newgeometry{headheight=10ex,inner=2cm,
	outer=2cm, % Outer margin
	bindingoffset=.5cm, % Binding offset
	top=2.5cm, % Top margin
	bottom=2cm ,twoside}}
        }  
        {
        \newcommand{\cambio}{
        \newgeometry{headheight=10ex,inner=2cm,
	outer=2cm, % Outer margin
	bindingoffset=.5cm, % Binding offset
	top=2.5cm, % Top margin
	bottom=2cm}
        }
        }
}

%%%%%%%%%%%%%%%%%%%%%%% <- FIN C. GENERALES

%%%%%%%%%%%%%%%%%%%%%%% <- MOD. Cap/Sec

\usepackage{xcolor}
\definecolor{lechuga}{RGB}{39, 30, 32}
\definecolor{azulsection}{RGB}{39, 30, 32}
\definecolor{verdesection}{RGB}{39, 30, 32}
\definecolor{grissection}{HTML}{6D6E71}
\definecolor{redi}{RGB}{39, 30, 32}
%e3254a
\definecolor{good_black}{RGB}{36, 30, 32}
\definecolor{good_green}{RGB}{109, 191, 81}
\newcommand{\capitulo}[2]{
    \chapter*{Chapter #1. #2}    \addcontentsline{toc}{chapter}{\protect\numberline{#1}#2}}
\newcommand{\bajavision}[1]{
 \ifthenelse{\equal{#1}{si}}{
    \newcommand{\estilopagina}{
        \pagecolor{good_black}
        \color{good_green}
    }
    \newcommand{\palitos}{
        \color{good_green}{\rule[0.5ex]{\linewidth}{2pt}\vspace*{-\baselineskip}\vspace*{3.2pt}\\
            \rule[0.2ex]{\linewidth}{2pt}\\
            [1mm]}
    }
    \newcommand{\logoUCM}{
        \includegraphics[width=0.65\textwidth]{LOGOS/logo_UCM_LV.png}
    }
}{ \newcommand{\estilopagina}{}
    \newcommand{\palitos}{
        \rule[0.5ex]{\linewidth}{2pt}\vspace*{-\baselineskip}\vspace*{3.2pt}\\
            \rule[0.2ex]{\linewidth}{2pt}\\
            [1mm]
    }
    \newcommand{\logoUCM}{
        \includegraphics[width=0.65\textwidth]{LOGOS/logo_UCM.jpg}
    }
}
}
\newcommand{\abstract}[1]{

 \ifthenelse{\equal{#1}{si}}
    {\newcommand{\insercion}{
            \input{Anexos/resumen.tex
        }
    }}
    {
        \newcommand{\insercion}{
        }
    }
}
\newcommand{\indicefiguras}[1]{

 \ifthenelse{\equal{#1}{si}}
    {\newcommand{\figuracion}{
            \listoffigures
        }
    }
    {
        \newcommand{\figuracion}{
        }
    }
}
\newcommand{\figuras}[3]{
\begin{figure}[H]
    \centering
    \includegraphics[width=0.45\textwidth]{#1}
    \includegraphics[width=0.45\textwidth]{#2}
    \ifthenelse{\equal{#3}{}}
    {}
    {
        \caption{#3}
        \label{fig:#3}
    }
\end{figure}
}

\newcommand{\figura}[3]{
\begin{figure}[H]
    \centering
    \ifthenelse{\equal{#2}{}} {\includegraphics[width=\textwidth]{#1}}{\includegraphics[width=#2\textwidth]{#1}}

    \ifthenelse{\equal{#3}{}}
    {}
    {
        \caption{#3}
        \label{fig:#3}
    }
\end{figure}
}
\newcommand{\indicetablas}[1]{

 \ifthenelse{\equal{#1}{si}}
    {\newcommand{\tabloides}{
            \listoftables
        }
    }
    {
        \newcommand{\tabloides}{
        }
    }
}
\newcommand{\autoria}[2]{
    \ifthenelse{\equal{#2}{no}}
    {#1 \\ \phantom{a}}
    {#1 \\ #2}
}

\newcommand{\direccion}[3]{
    \ifthenelse{\equal{#3}{no}}
    {\ifthenelse{\equal{#2}{no}}
    {#1 \\ \phantom{a} \\ \phantom{a}}
    {#1 \\ #2 \\ \phantom{a}}}
    {#1 \\ #2 \\ #3}
}

\usepackage{titlesec}


\titleformat{\chapter}[hang]
{\Huge\bfseries\color{lechuga}}
{\color{lechuga} Capítulo \thechapter. }
{0em}
{}
\titlespacing{\chapter}{0pt}{0pt}{0pt}
\titlespacing{\section}{0pt}{0pt}{0pt}
\titlespacing{\subsection}{0pt}{0pt}{0pt}
\titlespacing{\subsubsection}{0pt}{0pt}{0pt}

\titleformat{\section}[hang]
{\Large\bfseries\color{azulsection}}
{\color{azulsection} \thesection. }
{0em}
{}

\titleformat{\subsection}[hang]
{\Large\bfseries\color{verdesection}}
{\color{verdesection} \thesubsection. }
{0em}
{}


\titleformat{\subsubsection}[hang]
{\Large\bfseries\color{grissection}}
{\color{grissection}}
{0em}
{}

%%%%%%%%%%%%%%%%%%%%%%% <- GENERAMOS EL ÍNDICE
\usepackage{titletoc}% http://ctan.org/pkg/titletoc
\newcommand{\indiceTFG}{
    \setcounter{tocdepth}{0}
    \tableofcontents  
}

\titlecontents{chapter}% Comando a modificar
[0pt]% Espacio a la izquierda
{}% CÓDIGOS A LA IZQUIERDA
{\sffamily\bfseries\chaptername\phantom{l}\thecontentslabel\quad\quad}
{}
{\sffamily\bfseries\color{gray}\dotfill\color{black}\contentspage}


%%%%%%%%%%%%%%%%%%%%%%% <- FIN DE ÍNDICE

%%%%%%%%%%%%%%%%%%%%%%% <- FancyHDR

\usepackage{fancyhdr}
\fancyhead[LE,RO]{\thepage}
\fancyhead[LO,RE]{}
\fancyfoot[CE,CO]{}
\fancyfoot[LE,RO]{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

%%%%%%%%%%%%%%%%%%%%%%% <- Fin de FancyHDR

%%%%%%%%%%%%%%%%%%%%%%%%% <--- FINAL DE LA PLANTILLA
\newcommand{\bibliografia}{
    \figuracion
    \tabloides
    \bibliographystyle{IEEEtran}
    \bibliography{biblio}
    \addcontentsline{toc}{chapter}{\textsf{\textbf{Bibliografía}}}
}
\usepackage{emptypage}
%\usepackage[none]{hyphenat} % Desactiva la división de palabras
\usepackage{hyphenat} % Desactiva la división de palabras
\sloppy % Permite un espaciado más flexible para evitar overflow de texto

\newcommand*{\portada}[3]{
    \hypersetup{
        colorlinks=true,
        linkcolor=blue,
        filecolor=magenta,      
        urlcolor=cyan,
        pdftitle={#1},
        pdfpagemode=FullScreen,
    }
    \pagenumbering{roman}
    \thispagestyle{empty}
    \newgeometry{left=0in, right=0in, top=0in, foot=0in, bottom=-1.2em}
    \afterpage{\restoregeometry}
    \begin{figure}[H]
        \fboxsep25pt
        \colorbox{redi}{
        \begin{minipage}{20cm}
            \vspace*{-0.35cm}
              \begin{flushright}
                    \Large
                    \vspace{0.3em}
                    \color{white}
                    \textbf{Facultad de Informática}\phantom{a}\\
                    
                    \vspace{0.9em}
                    \textbf{Trabajo de Fin de Máster}\phantom{a}
                \end{flushright}
            \begin{minipage}{20cm}
            \vspace*{-3.6cm}
                \begin{figure}[H]
                      \hspace*{-0.9cm} \includegraphics[width=0.14\textwidth]{LOGOS/EO1.png}
                \end{figure}
            \end{minipage}
                \vspace*{-1.5cm}
        \end{minipage}
        }       
        \begin{figure}[H]
            \hspace*{0.13\textwidth}
            \begin{minipage}{15cm}
            \estilopagina
                \centering
            {\textbf{\Huge{#1}}}
            \end{minipage}
            \newgeometry{right=0in, left=0in}
            \palitos
            \centering
            \\ \Large Por\\ #2\\ \phantom{a}
            \begin{minipage}{21cm}
            \vspace*{0.05\textwidth}
            \centering
            \logoUCM
            \end{minipage}
        \end{figure}
        \estilopagina
        \vspace*{0.05\textwidth}
        \large
        \centering
        %\textit{Dirigido por}\\[1cm]
        #3\\\phantom{a}\\\phantom{a}\\[0.6cm]
        MADRID, 2025--2026
        
        
    \end{figure}  
    \cambio
    \pagestyle{fancy}
    \estilopagina

}
\newcommand{\maquetacion}[3]{
    \portada{#1}{#2}{#3}
    \insercion
    \indiceTFG
}
\newcommand{\clave}[1]{
    \addcontentsline{toc}{chapter}{\textbf{\textsf{Abstract}}}
    
    \vspace{\fill}
    \large
    \textbf{\textsf{Palabras Clave: #1}.}
}

\usepackage{xcolor}
\colorlet{mdtRed}{red!50!black}

\RequirePackage{hyperref}
\usepackage{multicol}
\hypersetup{pdfpagemode={UseOutlines},
bookmarksopen=true,
bookmarksopenlevel=0,
hypertexnames=false,
colorlinks=true,% Set to false to disable coloring links
citecolor=magenta,% The color of citations
linkcolor=blue,% The color of references to document elements (sections, figures, etc)
urlcolor=mdtRed,% The color of hyperlinks (URLs)
pdfstartview={FitV},
unicode,
breaklinks=true,
}

\doublehyphendemerits=10000 % No consecutive line hyphens
\brokenpenalty=10000 % No broken words across columns/pages
\widowpenalty=9999 % Almost no widows at bottom of page
\clubpenalty=9999 % Almost no orphans at top of page
\interfootnotelinepenalty=9999 % Almost never break footnotes

\RequirePackage{silence}
\WarningsOff[fancyhdr]
\WarningsOff[crimson]
\WarningsOff[fontenc]
\WarningsOff[babel]
\WarningsOff[latex]
\endinput