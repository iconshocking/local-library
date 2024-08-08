const fadein = document.querySelector("#final-fadein-on-scroll");
if (!fadein) {
  throw new Error("No element with id 'final-fadein-on-scroll' found");
}

let observer = new IntersectionObserver(
  (entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.remove("opacity-0");
        entry.target.classList.add("fadein");
        observer.unobserve(entry.target);
      }
    });
  },
  {
    threshold: 1.0,
  }
);

observer.observe(fadein);
