class ImageSpec {
  prompt string
  style string
  aspect_ratio string
}

function ParseImageRequest(message: string, style_guide: string) -> ImageSpec {
  client Anthropic
  prompt #"
    {{ _.role("system") }}
    Convert the request into an image-generation spec.
    Style guide: {{ style_guide }}
    aspect_ratio must be one of: square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9.

    {{ _.role("user") }}
    {{ message }}

    {{ ctx.output_format }}
  "#
}
