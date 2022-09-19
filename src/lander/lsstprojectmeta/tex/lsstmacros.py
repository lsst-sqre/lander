"""LaTeX macros provided by the lsstdoc class.

lsstprojectmeta mirrors these macros to allow Pandoc to resolve them.
"""

__all__ = ["LSSTDOC_MACROS"]

LSSTDOC_MACROS = r"""\newcommand{\latex}{LaTeX}
\newcommand{\docType}{LSST Document}
\newcommand{\CU}{DM}
\newcommand{\DU}{}
\newcommand{\setLSSTDU}[1]{\renewcommand{\DU}{-#1}}
\newcommand{\byte}{b}
\def\aaps{A\&AS}           % Astronomy and Astrophysics Suplement
\def\aap{A\&A}             % Astronomy and Astrophysics
\def\ssr{Space~Sci.~Rev.}  % Space Science Reviews
\def\apj{ApJ}              % Astrophysical Journal
\def\apjs{ApJS}            % Astrophysical Journal Supplement
\def\aj{AJ}                % Astronomical Journal
\def\mnras{MNRAS}          % Monthly Notices of the RAS
\def\araa{ARA\&A}          % Annual Review of Astron and Astrophys
\def\nat{Nature}           % Nature
\def\apjl{ApJ}             % Astrophysical Journal, Letters
\def\icarus{Icarus}        % Icarus
\def\prd{Phys.~Rev.~D}     % Physical Review D
\def\physrep{Phys.~Rep.}   % Physics Reports
\def\pasp{PASP}            % Publications of the Astronomical Society of the Pacific
\def\procspie{Proc.\ SPIE} % Proceedings of the SPIE
\newcommand{\pasa}{PASA}   % Publications of the Astronomical Society of Australia
\newcommand{\ao}{Appl.~Opt.}  % Applied Optics

\def\degr{\hbox{$^\circ$}}
\def\arcmin{\hbox{$^\prime$}}
\def\arcsec{\hbox{$^{\prime\prime}$}}
\def\fs{\hbox{$.\!\!^{\rm s}$}}
\def\fdg{\hbox{$.\!\!^\circ$}}
\def\farcm{\hbox{$.\mkern-4mu^\prime$}}
\def\farcs{\hbox{$.\!\!^{\prime\prime}$}}
\def\sun{\hbox{$\odot$}}
\newcommand{\pu}[2]{\ensuremath{#1\,\mbox{#2}}}
\newcommand{\secs}[1]{\pu{#1}{s}}
\newcommand{\uas}[1]{\pu{#1}{$\mu$as}}
\newcommand{\muas}[1]{\pu{#1}{$\mu$as}}
\newcommand{\muasonly}{\ensuremath{\mu\mbox{as}}}
\newcommand{\inp}[1]{{\tt #1}}
\newcommand{\prog}[1]{{\it #1}}
\newcommand{\secref}[1]{Section~\ref{#1}}
\newcommand{\appref}[1]{Appendix~\ref{#1}}
\newcommand{\partref}[1]{Part~\ref{#1}}
\newcommand{\tabref}[1]{Table~\ref{#1}}
\newcommand{\figref}[1]{Figure~\ref{#1}}
\newcommand{\eqnref}[1]{Eq.~\ref{#1}}
\newcommand{\reqref}[1]{Req.~\ref{#1}}
\newcommand{\actref}[1]{AI~\ref{#1}}
\newcommand{\class}[1]{{\it #1}}
\newcommand{\pack}[1]{{\em #1}}
\newcommand{\property}[1]{{\em #1}}
\newcommand{\method}[1]{{\em #1}}
\newcommand{\file}[1]{{\em #1}}
\newcommand{\directory}[1]{{\em #1}}
%\providecommand{\code}[1]{{\tt #1}}

% \renewcommand{\vec}[1]{\ensuremath{\mathchoice{\mbox{\boldmath$\displaystyle#1$}}
% {\mbox{\boldmath$\textstyle#1$}}
% {\mbox{\boldmath$\scriptstyle#1$}}
% {\mbox{\boldmath$\scriptscriptstyle#1$}}}}

\newcommand{\vstretch}[1]{\vspace*{\stretch{#1}}}
\newcommand{\code}[1]{\texttt{#1}}

\newcommand{\Alert}{\code{Alert}\xspace}
\newcommand{\Alerts}{\code{Alerts}\xspace}
\newcommand{\DIASource}{\code{DIA\-Source}\xspace}
\newcommand{\DIASources}{\code{DIA\-Sources}\xspace}
\newcommand{\DIAObject}{\code{DIA\-Object}\xspace}
\newcommand{\DIAObjects}{\code{DIA\-Objects}\xspace}
\newcommand{\DB}{{Level 1 database}\xspace}
\newcommand{\DR}{{Level 2 database}\xspace}
\newcommand{\Object}{\code{Object}\xspace}
\newcommand{\Objects}{\code{Objects}\xspace}
\newcommand{\Source}{\code{Source}\xspace}
\newcommand{\Sources}{\code{Sources}\xspace}
\newcommand{\ForcedSource}{\code{Forced\-Source}\xspace}
\newcommand{\ForcedSources}{\code{Forced\-Sources}\xspace}
\newcommand{\CoaddSource}{\code{Coadd\-Source}\xspace}
\newcommand{\CoaddSources}{\code{Coadd\-Sources}\xspace}
\newcommand{\SSObject}{\code{SS\-Object}\xspace}
\newcommand{\SSObjects}{\code{SS\-Objects}\xspace}
\newcommand{\VOEvent}{\code{VO\-Event}\xspace}
\newcommand{\VOEvents}{\code{VO\-Events}\xspace}
\newcommand{\transSNR}{5\xspace}

% Command to link to a document in Docushare. Pass an LSST document handle as argument, or a document number.
% This will not result in a references entry.
\newcommand{\ds}[2]{{\color{blue} \href{https://docushare.lsst.org/docushare/dsweb/Get/#1}{#2}}\xspace}

% These used to be `citeds` commands. Now just plain text with hyperlinks.
\newcommand{\SRD}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LPM-17}{SRD}\xspace}
\newcommand{\DPDD}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LSE-163}{DPDD}\xspace}
\newcommand{\LSR}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LSE-29}{LSR}\xspace}
\newcommand{\OSS}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LSE-30}{OSS}\xspace}
\newcommand{\DMSR}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LSE-61}{DMSR}\xspace}
\newcommand{\appsUMLdomain}{https://docushare.lsst.org/docushare/dsweb/Get/\href{LDM-133}{LDM-133}\xspace}
\newcommand{\appsUMLusecase}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LDM-134}{LDM-134}\xspace}
\newcommand{\SUI}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LDM-131}{SUID}\xspace}
\newcommand{\DMSD}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LDM-148}{DMSD}\xspace}
\newcommand{\MOPSD}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LDM-156}{MOPSD}\xspace}
\newcommand{\DMMD}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LDM-152}{DMMD}\xspace}
\newcommand{\DMOps}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LDM-230}{DM OpsCon}\xspace}
\newcommand{\SDQAP}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LSE-63}{LSE-63}\xspace}
\newcommand{\NewPCP}{\href{https://docushare.lsst.org/docushare/dsweb/Get/LSE-180}{LSE-180}\xspace}
\newcommand{\UCAL}{\href{https://docushare.lsst.org/docushare/dsweb/Get/Document-15125}{UCAL}\xspace}

\newcommand{\wbsSFM}{WBS 02C.03.01}
\newcommand{\wbsAssocP}{WBS 02C.03.02}
\newcommand{\wbsAP}{WBS 02C.03.03}
\newcommand{\wbsDiffim}{WBS 02C.03.04}
\newcommand{\wbsMOPS}{WBS 02C.03.06}
\newcommand{\wbsSDQAP}{WBS 02C.01.02.02}
\newcommand{\wbsSDQAT}{WBS 02C.01.02.02}
\newcommand{\wbsSPT}{WBS 02C.01.02.03}
\newcommand{\wbsPSF}{WBS 02C.04.03}
\newcommand{\wbsCoadd}{WBS 02C.04.04}
\newcommand{\wbsDetDeblend}{WBS 02C.04.05}
\newcommand{\wbsObjChar}{WBS 02C.04.06}
\newcommand{\wbsAFW}{WBS 02C.03.05, 02C.04.01}
\newcommand{\wbsCPP}{WBS 02C.04.02}
\newcommand{\wbsPhotoCal}{WBS 02C.03.07}
\newcommand{\wbsAstroCal}{WBS 02C.03.08}

%%% Command's for merging Robert's document, at least temporarily.
%%% Some of these will be removable, some may not be.
\renewcommand{\c}{\textit{c.}\xspace}
\newcommand{\eg}{\textit{e.g.}\xspace}
\newcommand{\etc}{\textit{etc.}\xspace}
\newcommand{\ie}{\textit{i.e.}\xspace}
\renewcommand{\th}{\ensuremath{^{\mbox{\tiny th}}}\xspace}
\newcommand{\Nb}{\textit{N.b.}\xspace}
\newcommand{\nb}{\textit{n.b.}\xspace}
\DeclareBoldMathCommand\xib{\xi}
\DeclareBoldMathCommand\zerob{0}
\newcommand{\cameraTeam}{\textbf{Camera Team deliverable}\\}
\newcommand{\TBD}{\textit{T.B.D.}\xspace}
\newcommand{\myLabel}[2]{\def\@currentlabel{#2}\label{#1}}
\newcommand{\appRef}[1]{App. \ref{app:#1}}
\newcommand{\secRef}[1]{Sec. \ref{sec:#1}}
\newcommand{\rednote}[1]{{\color{red} (#1)}}

\newcommand{\alg}{\\ \textbullet\xspace Algorithmic component: }
\newcommand{\fefiftyfive}{$^{55}$Fe\xspace}
\newcommand{\bfeffect}{``brighter-fatter effect"}
\newcommand{\auxtelescope}{auxiliary/Calpyso/calibration telescope\xspace}
\newcommand{\secsymbol}{§}
\newcommand{\xxx}{{\color{red} xxx}\xspace}
\newcommand{\dragons}{ {\color{blue} \textbf{\textit{Here be dragons...}}}}
\newcommand{\mysubitem}{\subitem \textendash\xspace}
\newcommand{\smalltilde}{\raise.26ex\hbox{$\scriptstyle\mathtt{\sim}$}}
\newcommand{\electron}{$e^{-}$}

\newcommand{\oldtext}[1]{{\color{red} #1}}
\newcommand{\newtext}[1]{{\color{blue} #1}}

\newcommand{\jira}[1]{\href{https://jira.lsstcorp.org/browse/#1}{#1}}

\newcommand{\uc}[1]{\texttt{#1}}
"""
