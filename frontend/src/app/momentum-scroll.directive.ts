import { DOCUMENT } from '@angular/common';
import { Directive, ElementRef, Inject, OnInit } from '@angular/core';

@Directive({
  selector: '[appMomentumScroll]'
})
export class MomentumScrollDirective implements OnInit {
  private data = {
    ease: 0.1,
    curr: 0,
    prev: 0,
    rounded: 0,
  };

  private parentNodeStyles = {
    position: 'fixed',
    top: '0',
    left: '0',
    height: '100%',
    width: '100%',
    overflow: 'hidden',
    pointerEvents: 'none',
  } as CSSStyleDeclaration;


  constructor(private el: ElementRef<HTMLElement>, @Inject(DOCUMENT) private document: Document) { }

  ngOnInit(): void {
    requestAnimationFrame(() => this.smoothScroll());
  }

  private get elementInitialized(): boolean{
    return !!(this.el && this.el.nativeElement);
  }

  private smoothScroll(): void {
    if (this.elementInitialized) {
      this.data.curr = window.scrollY;
      this.data.prev += (this.data.curr - this.data.prev) * this.data.ease;
      this.data.rounded = Math.round(this.data.prev * 100) / 100;

      this.el.nativeElement.style.transform = `translate3d(0, -${this.data.rounded}px, 0)`;

      requestAnimationFrame(() => this.smoothScroll());
    }
  }
}
