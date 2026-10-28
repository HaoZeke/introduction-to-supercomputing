;;; export.el --- export the deck to beamer LaTeX  -*- lexical-binding: t; -*-
;; Org beamer turns *bold* into \alert; this deck wants plain bold.
(require 'ox-beamer)
;; Scalable math fonts support the deck's explicit text-box sizes.
(let ((class (assoc "beamer" org-latex-classes)))
  (setf (nth 1 class) (concat "\\RequirePackage{fix-cm}\n" (nth 1 class))))
(defun pptx-deck-bold (_bold contents _info)
  (format "\\textbf{%s}" contents))
(advice-add 'org-beamer-bold :override #'pptx-deck-bold)
(org-beamer-export-to-latex)
